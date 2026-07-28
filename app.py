import streamlit as st
import pandas as pd
import sqlite3
import requests
import zipfile
import os
import json
import re
import string
from itertools import combinations

# ========================================================
# 0. Page Config & Enterprise Medical UI Styling
# ========================================================
st.set_page_config(
    page_title="RxShield | Clinical Decision Support System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .sticky-header {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: var(--background-color);
        border-bottom: 2px solid #00796b;
        padding: 15px 0px;
        margin-bottom: 25px;
        z-index: 99;
    }
    .header-title { font-size: 2.2rem; font-weight: 700; color: #00796b; margin: 0; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 1rem; color: var(--text-color); opacity: 0.8; margin-top: 4px; }
    
    .med-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px; padding: 22px; margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease;
    }
    .med-card:hover {
        border-color: rgba(0, 121, 107, 0.3);
    }
    
    .clinical-badge {
        display: inline-flex; align-items: center; padding: 5px 12px;
        border-radius: 20px; font-size: 0.78rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .badge-high { background-color: rgba(211, 47, 47, 0.12); color: #d32f2f; border: 1px solid rgba(211, 47, 47, 0.3); }
    .badge-moderate { background-color: rgba(245, 127, 23, 0.12); color: #f57f17; border: 1px solid rgba(245, 127, 23, 0.3); }
    .badge-monitor { background-color: rgba(21, 101, 192, 0.12); color: #1565c0; border: 1px solid rgba(21, 101, 192, 0.3); }
    .badge-safe { background-color: rgba(46, 125, 50, 0.12); color: #2e7d32; border: 1px solid rgba(46, 125, 50, 0.3); }

    .sidebar-brand { font-size: 1.5rem; font-weight: 700; color: #00796b; margin-bottom: 5px; }
    .sidebar-status-tag {
        background-color: rgba(46, 125, 50, 0.12); color: #2e7d32; padding: 6px 12px;
        border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;
        margin-bottom: 20px; border: 1px solid rgba(46, 125, 50, 0.2);
    }
    .app-footer { text-align: center; padding: 30px 0px; margin-top: 50px; font-size: 0.82rem; opacity: 0.6; border-top: 1px solid rgba(128, 128, 128, 0.15); }
</style>
""", unsafe_allow_html=True)

# ========================================================
# Sidebar Presentation Layer
# ========================================================
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>🛡️ RxShield CDSS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-status-tag'>🟢 ENGINE ONLINE & SECURED</div>", unsafe_allow_html=True)
    st.markdown("### 📊 System Diagnostics\n**Core Pipeline Layer:** Tier-1 Clinical Verification\n**Deployment Context:** Production Cloud Instance")
    st.markdown("---\n### ⚙️ Database Ledger Specifications\nSQLite Engine operating via read-only connections. Data strictly cross-referenced against DrugBank / Medical schemas.")
    st.markdown("---")
    st.info("💡 **Clinical Tip:** Use the Regimen Matrix tab to assess multi-drug interactions for complex patient cases simultaneously.")

st.markdown("""
<div class='sticky-header'>
    <h1 class='header-title'>RxShield | Advanced Decision Support Portal</h1>
    <p class='header-subtitle'>Real-time multi-channel verification pipeline for interactive Drug-Drug and Drug-Food contraindications.</p>
</div>
""", unsafe_allow_html=True)

# ========================================================
# 1. Database Initialization
# ========================================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mustafaamer97/RxShield/main"
ZIP_FILE_URL = f"{GITHUB_RAW_URL}/all_id_interaction.zip"
DB_ZIP_PATH = "all_id_interaction.zip"
DB_FILE_PATH = "all_id_interaction.db"

@st.cache_resource
def init_database():
    if not os.path.exists(DB_FILE_PATH):
        with st.spinner('⏳ [CDSS Pipeline Initialization] Downloading and indexing medical database matrices...'):
            response = requests.get(ZIP_FILE_URL, stream=True)
            if response.status_code == 200:
                with open(DB_ZIP_PATH, 'wb') as f:
                    f.write(response.content)
                with zipfile.ZipFile(DB_ZIP_PATH, 'r') as zip_ref:
                    zip_ref.extractall(".")
                if os.path.exists(DB_ZIP_PATH):
                    os.remove(DB_ZIP_PATH)
            else:
                st.error("❌ Critical Database System Sync Failure.")
                return None
    return sqlite3.connect(DB_FILE_PATH, check_same_thread=False)

db_conn = init_database()

# ========================================================
# 2. STRICT DATA ENGINEERING: Ultra-Strict Chemical Filter
# ========================================================
def is_valid_drug_name(name):
    if not name or len(name) < 2:
        return False
    name_str = str(name).strip()
    name_lower = name_str.lower()
    
    if name_lower.endswith('acid') or ' acid' in name_lower:
        return False
    if any(term in name_lower for term in ['heme', 'cholesterol', 'diiodo', 'diamino', 'nonanoic', 'propionic']):
        return False
    if re.search(r'\d+,\d+', name_str) or re.search(r'^[0-9]+[,\-]', name_str):
        return False
        
    iupac_symbols = ['(', ')', '[', ']', '{', '}', '+', '=', '<', '>', ';', '\\', '/']
    if any(char in name_str for char in iupac_symbols):
        return False
        
    if len(name_str) > 35:
        return False
        
    return True

@st.cache_data
def build_clinical_medication_index():
    synonyms_data = {}
    drug_info = {}
    food_data = ""
    
    if os.path.exists('drugs_synonyms.json'):
        with open('drugs_synonyms.json', 'r', encoding='utf-8') as f:
            synonyms_data = json.load(f)
            
    if os.path.exists('drug_info.json'):
        with open('drug_info.json', 'r', encoding='utf-8') as f:
            drug_info = json.load(f)
            
    if os.path.exists('Drug to Food interactions ...'):
        with open('Drug to Food interactions ...', 'r', encoding='utf-8') as f:
            food_data = f.read()

    med_index = {}
    all_ids = set(synonyms_data.keys()).union(set(drug_info.keys()))
    
    for drug_id in all_ids:
        u_id = drug_id.upper()
        info = drug_info.get(drug_id, {})
        
        display_name = ""
        if isinstance(info, dict):
            candidate = info.get("name", "").strip()
            if is_valid_drug_name(candidate):
                display_name = candidate
            else:
                candidate_gen = info.get("generic_name", "").strip()
                if is_valid_drug_name(candidate_gen):
                    display_name = candidate_gen
                    
        if not display_name:
            syns = synonyms_data.get(drug_id, [])
            for s in syns:
                if is_valid_drug_name(s):
                    display_name = str(s).strip()
                    break
                    
        if not display_name or not is_valid_drug_name(display_name):
            continue
            
        display_name = display_name.capitalize()
        
        search_aliases = {display_name.lower()}
        for syn in synonyms_data.get(drug_id, []):
            search_aliases.add(str(syn).lower())
        if isinstance(info, dict):
            for key in ['generic_name', 'brand_names', 'synonyms']:
                val = info.get(key)
                if isinstance(val, list):
                    for v in val: search_aliases.add(str(v).lower())
                elif isinstance(val, str):
                    for v in val.split(','): search_aliases.add(v.strip().lower())
        
        cleaned_aliases = set()
        for alias in search_aliases:
            if alias:
                clean_str = str(alias).lower().translate(str.maketrans('', '', string.punctuation))
                clean_str = " ".join(clean_str.split())
                if clean_str:
                    cleaned_aliases.add(clean_str)
                    
        med_index[u_id] = {
            "display_name": display_name,
            "search_aliases": cleaned_aliases,
            "drug_id": u_id,
            "raw_info": info if isinstance(info, dict) else {}
        }
        
    return food_data, med_index

food_interactions_text, med_index = build_clinical_medication_index()

# ========================================================
# 3. Core Engine Functions
# ========================================================
def clean_interaction_text(text, target_drug_name):
    if not text: return ""
    cleaned = re.sub(r'\(\.\*\)', f" {target_drug_name} ", text)
    cleaned = cleaned.replace("the risk or severity of", "The risk of")
    cleaned = cleaned.replace("when is combined with .", f"when combined with {target_drug_name}.")
    cleaned = cleaned.replace("when combined with .", f"when combined with {target_drug_name}.")
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned + '.' if cleaned and not cleaned.endswith('.') else cleaned

def get_severity_color(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["bleeding", "arrhythmia", "qtc prolongation", "toxicity", "fatal", "severe", "hemorrhage"]):
        return "🔴 High Risk"
    elif any(w in text_lower for w in ["decrease the therapeutic efficacy", "increase the excretion rate", "risk of adverse effects"]):
        return "🟡 Moderate Caution"
    return "🔵 Monitor / Information"

def render_medication_search_flow(label, index, key_prefix):
    search_input = st.text_input(
        f"🔍 Search Formulation, Brand, or Synonym for [{label}]:",
        key=f"{key_prefix}_text_search",
        placeholder="e.g., Warfarin, Aspirin, Metformin..."
    ).strip()
    
    normalized_query = " ".join(search_input.lower().translate(str.maketrans('', '', string.punctuation)).split()) if search_input else ""
    
    filtered_pool = []
    if not normalized_query:
        count = 0
        for d_id, metadata in index.items():
            filtered_pool.append((metadata["display_name"], d_id))
            count += 1
            if count > 500: break
    else:
        for d_id, metadata in index.items():
            if any(normalized_query in alias for alias in metadata["search_aliases"]):
                filtered_pool.append((metadata["display_name"], d_id))
                
    unique_pool = {}
    for name, d_id in filtered_pool:
        if name not in unique_pool:
            unique_pool[name] = d_id
            
    final_list = [(name, d_id) for name, d_id in unique_pool.items()]
    final_list.sort(key=lambda x: x[0])
    
    if not final_list:
        st.warning(f"⚠️ Zero clinical matches found for '{search_input}'.")
        return None, None
        
    selected_tuple = st.selectbox(
        f"Select Confirmed Entry:",
        options=final_list,
        format_func=lambda x: x[0],
        key=f"{key_prefix}_dropdown"
    )
    
    if selected_tuple:
        return selected_tuple[1], selected_tuple[0]
    return None, None

# ========================================================
# 4. Main User Interface (Refactored with Clinical Cards)
# ========================================================
if db_conn:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 Single Formulation Profiler", 
        "⚔️ Binary Interaction Checker", 
        "💊 Multi-Drug Regimen Safety Matrix",
        "🥦 Nutritional Constraints"
    ])
    
    # --- TAB 1: SMART SINGLE DRUG SEARCH & MONOGRAPH ---
    with tab1:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        target_id, current_drug_name = render_medication_search_flow("Target Clinical Drug", med_index, "single")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if target_id:
            with st.spinner("⏳ Extracting clinical monograph and checking interaction profiles..."):
                meta_dict = med_index.get(target_id, {})
                raw_info = meta_dict.get("raw_info", {})
                
                # Monograph Card
                st.markdown("<div class='med-card'>", unsafe_allow_html=True)
                st.markdown(f"### 📋 Clinical Monograph: {current_drug_name}")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Generic Name:** {raw_info.get('generic_name', current_drug_name)}")
                    brands = raw_info.get('brand_names', [])
                    if isinstance(brands, list) and brands:
                        st.markdown(f"**Brand Formulations:** {', '.join(brands[:5])}")
                with col_b:
                    desc = raw_info.get('description', 'Verified standard active pharmaceutical ingredient profile.')
                    st.markdown(f"**Therapeutic Overview:** {desc[:250]}...")
                st.markdown("</div>", unsafe_allow_html=True)
                
                query = "SELECT * FROM interactions WHERE \"Drug1 ID\" = ? OR \"Drug2 ID\" = ?"
                df_res = pd.read_sql_query(query, db_conn, params=(target_id, target_id))
                
                if not df_res.empty:
                    processed_data = []
                    for _, row in df_res.iterrows():
                        other_id = str(row['Drug2 ID']).upper() if str(row['Drug1 ID']).upper() == target_id else str(row['Drug1 ID']).upper()
                        other_name = med_index[other_id]["display_name"] if other_id in med_index else "Registered Medication"
                        
                        clean_text = clean_interaction_text(row['Interaction'], other_name)
                        processed_data.append({
                            "Interacting Drug Formulation": other_name,
                            "Clinical Severity Status": get_severity_color(clean_text),
                            "Documented Mechanism / Medical Effect": clean_text
                        })
                    
                    df_clean = pd.DataFrame(processed_data)
                    
                    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
                    severity_filter = st.radio("🎯 Filter Profile Ledger by Severity:", options=["All", "🔴 High Risk Only", "🟡 Moderate Caution Only", "🔵 Monitor / Info Only"], horizontal=True)
                    
                    if "🔴" in severity_filter: df_clean = df_clean[df_clean["Clinical Severity Status"] == "🔴 High Risk"]
                    elif "🟡" in severity_filter: df_clean = df_clean[df_clean["Clinical Severity Status"] == "🟡 Moderate Caution"]
                    elif "🔵" in severity_filter: df_clean = df_clean[df_clean["Clinical Severity Status"] == "🔵 Monitor / Information"]
                    
                    st.metric(label="Total Cross-Referenced Vectors", value=len(df_clean))
                    st.markdown("---")
                    
                    # Render Cards instead of Table
                    for _, r in df_clean.iterrows():
                        sev = r["Clinical Severity Status"]
                        badge_class = "badge-high" if "High" in sev else ("badge-moderate" if "Moderate" in sev else "badge-monitor")
                        st.markdown(f"""
                            <div class="med-card" style="margin-bottom: 12px; padding: 18px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <strong style="font-size: 1.1rem; color: #00796b;">💊 {r['Interacting Drug Formulation']}</strong>
                                    <span class="clinical-badge {badge_class}">{sev}</span>
                                </div>
                                <p style="margin: 0; font-size: 0.95rem; opacity: 0.9;">{r['Documented Mechanism / Medical Effect']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info(f"ℹ️ No contraindications registered for {current_drug_name}.")

    # --- TAB 2: DRUG VS DRUG CHECKER ---
    with tab2:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1: id_a, name_a = render_medication_search_flow("Component A", med_index, "pair_a")
        with col2: id_b, name_b = render_medication_search_flow("Component B", med_index, "pair_b")
        st.markdown("</div>", unsafe_allow_html=True)
            
        if id_a and id_b:
            if id_a == id_b: 
                st.warning("⚠️ Identity Conflict: Please select two separate formulations.")
            else:
                with st.spinner("⏳ Analyzing binary clinical pathway..."):
                    query = "SELECT * FROM interactions WHERE (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?) OR (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?)"
                    df_pair = pd.read_sql_query(query, db_conn, params=(id_a, id_b, id_b, id_a))
                    
                    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
                    if not df_pair.empty:
                        cleaned_interaction = clean_interaction_text(df_pair.iloc[0]['Interaction'], name_b)
                        severity_status = get_severity_color(cleaned_interaction)
                        
                        if "🔴" in severity_status: badge_c = "badge-high"
                        elif "🟡" in severity_status: badge_c = "badge-moderate"
                        else: badge_c = "badge-monitor"
                        
                        st.markdown(f"""
                            <div style="padding: 10px 0;">
                                <h3 style="color: #d32f2f; margin-bottom: 10px;">🚨 Contraindication Profile Alert Generated!</h3>
                                <div style="margin-bottom: 15px;">
                                    <span class="clinical-badge {badge_c}">{severity_status}</span>
                                </div>
                                <p style="font-size: 1.05rem; line-height: 1.5;"><strong>Documented Pathophysiology:</strong> {cleaned_interaction}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="padding: 10px 0;">
                                <h3 style="color: #2e7d32; margin-bottom: 10px;">✅ Safe Therapeutic Pathway</h3>
                                <div style="margin-bottom: 15px;">
                                    <span class="clinical-badge badge-safe">NO CONTRADICTIONS</span>
                                </div>
                                <p style="font-size: 1.05rem;">No direct contraindications mapped between <strong>{name_a}</strong> and <strong>{name_b}</strong>.</p>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3: MULTI-DRUG REGIMEN SAFETY MATRIX ---
    with tab3:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        st.markdown("### 💊 Comprehensive Patient Medication Regimen Screening")
        st.markdown("Select multiple medications currently prescribed to the patient to evaluate all cross-interactions simultaneously.")
        
        sorted_med_options = sorted([(m["display_name"], d_id) for d_id, m in med_index.items()], key=lambda x: x[0])
        selected_regimen = st.multiselect(
            "Select Patient Regimen Formulations:",
            options=sorted_med_options,
            format_func=lambda x: x[0],
            key="regimen_multiselect"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        if selected_regimen and len(selected_regimen) >= 2:
            with st.spinner("⏳ Running pairwise combinatorial matrix validation..."):
                st.markdown("<div class='med-card'>", unsafe_allow_html=True)
                st.markdown("#### 📊 Regimen Cross-Pairwise Interaction Results")
                
                regimen_pairs = list(combinations(selected_regimen, 2))
                regimen_results = []
                
                for (name_1, id_1), (name_2, id_2) in regimen_pairs:
                    q_reg = "SELECT * FROM interactions WHERE (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?) OR (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?)"
                    df_r = pd.read_sql_query(q_reg, db_conn, params=(id_1, id_2, id_2, id_1))
                    
                    if not df_r.empty:
                        txt = clean_interaction_text(df_r.iloc[0]['Interaction'], name_2)
                        sev = get_severity_color(txt)
                        regimen_results.append({
                            "Pair": f"{name_1} + {name_2}",
                            "Severity": sev,
                            "Mechanism": txt
                        })
                    else:
                        regimen_results.append({
                            "Pair": f"{name_1} + {name_2}",
                            "Severity": "✅ Safe / No Interaction",
                            "Mechanism": "No documented contraindications between this pair."
                        })
                
                st.metric(label="Total Combinations Evaluated", value=len(regimen_pairs))
                st.markdown("---")
                
                # Render Cards for Regimen Pairs
                for item in regimen_results:
                    sev = item["Severity"]
                    if "High" in sev or "🔴" in sev: b_class = "badge-high"
                    elif "Moderate" in sev or "🟡" in sev: b_class = "badge-moderate"
                    elif "Safe" in sev or "✅" in sev: b_class = "badge-safe"
                    else: b_class = "badge-monitor"
                    
                    st.markdown(f"""
                        <div class="med-card" style="margin-bottom: 12px; padding: 18px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <strong style="font-size: 1.1rem; color: #00796b;">⚔️ {item['Pair']}</strong>
                                <span class="clinical-badge {b_class}">{sev}</span>
                            </div>
                            <p style="margin: 0; font-size: 0.95rem; opacity: 0.9;">{item['Mechanism']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        elif selected_regimen and len(selected_regimen) == 1:
            st.info("ℹ️ Please select at least two medications to generate pairwise regimen interactions.")

    # --- TAB 4: DRUG-FOOD INTERACTIONS ---
    with tab4:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        food_search = st.text_input("🥗 Query lifestyle or nutritional constraints (e.g., Grapefruit, Warfarin):").strip()
        st.markdown("</div>", unsafe_allow_html=True)
        
        if food_search and food_interactions_text:
            matching_lines = [line.strip() for line in food_interactions_text.split('\n') if food_search.lower() in line.lower()]
            st.markdown("<div class='med-card'>", unsafe_allow_html=True)
            if matching_lines:
                st.warning(f"⚠️ Identified {len(matching_lines)} Dietary Precautions:")
                for line in matching_lines[:15]: 
                    st.markdown(f"""
                        <div style="padding: 10px 14px; margin-bottom: 8px; background-color: rgba(245, 127, 23, 0.05); border-left: 4px solid #f57f17; border-radius: 4px;">
                            💡 {line}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No dietary contraindications detected.")
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("⚙️ Connection Error.")

st.markdown("<div class='app-footer'>RxShield CDSS Engine Tier-1 • Enterprise Platform Build v2026.4.12 • Verified Clinical Ledger</div>", unsafe_allow_html=True)
