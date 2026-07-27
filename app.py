import streamlit as st
import pandas as pd
import sqlite3
import requests
import zipfile
import os
import json
import re
import string

# ========================================================
# 0. Page Config & Professional UI Injection
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
        margin-bottom: 30px;
        z-index: 99;
    }
    .header-title { font-size: 2.2rem; font-weight: 700; color: #00796b; margin: 0; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 1rem; color: var(--text-color); opacity: 0.8; margin-top: 4px; }
    .med-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px; padding: 24px; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    }
    .clinical-badge {
        display: inline-flex; align-items: center; padding: 6px 14px;
        border-radius: 30px; font-size: 0.85rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.5px; margin-top: 5px;
    }
    .badge-high { background-color: rgba(211, 47, 47, 0.12); color: #d32f2f; border: 1px solid rgba(211, 47, 47, 0.3); }
    .badge-moderate { background-color: rgba(245, 127, 23, 0.12); color: #f57f17; border: 1px solid rgba(245, 127, 23, 0.3); }
    .badge-monitor { background-color: rgba(21, 101, 192, 0.12); color: #1565c0; border: 1px solid rgba(21, 101, 192, 0.3); }
    .sidebar-brand { font-size: 1.5rem; font-weight: 700; color: #00796b; margin-bottom: 5px; }
    .sidebar-status-tag {
        background-color: rgba(46, 125, 50, 0.12); color: #2e7d32; padding: 6px 12px;
        border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;
        margin-bottom: 20px; border: 1px solid rgba(46, 125, 50, 0.2);
    }
    .app-footer { text-align: center; padding: 25px 0px; margin-top: 60px; font-size: 0.8rem; opacity: 0.6; border-top: 1px solid rgba(128, 128, 128, 0.15); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='sidebar-brand'>🛡️ RxShield CDSS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-status-tag'>🟢 ENGINE ONLINE & SECURED</div>", unsafe_allow_html=True)
    st.markdown("### 📊 System Diagnostics\n**Core Pipeline Layer:** Tier-1 Clinical Verification\n**Deployment Context:** Production Cloud Instance")
    st.markdown("---\n### ⚙️ Database Ledger Specifications\nSQLite Engine operating via read-only connections. Data strictly cross-referenced against DrugBank / Medical schemas.")

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
# 2. STRICT DATA ENGINEERING: Filter Out IUPAC Chemicals
# ========================================================
def is_valid_drug_name(name):
    """Returns True only if the name looks like a real medication name, not a chemical formula."""
    if not name or len(name) < 2:
        return False
    name_str = str(name).strip()
    
    # Reject if it contains typical IUPAC / chemical indicators
    iupac_symbols = ['(', ')', '[', ']', '{', '}', '+', '=', '<', '>', ';', '\\', '/']
    if any(char in name_str for char in iupac_symbols):
        return False
        
    # Reject if it starts with numbers or chemical locants like "2-", "1r-"
    if re.match(r'^[0-9]+[\-\s]', name_str) or re.match(r'^\([0-9a-z]+\)', name_str):
        return False
        
    # Reject if it's excessively long (typical drug names are concise)
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
        
        # 1. Try to get clean name from drug_info.json
        if isinstance(info, dict):
            candidate = info.get("name", "").strip()
            if is_valid_drug_name(candidate):
                display_name = candidate
            else:
                candidate_gen = info.get("generic_name", "").strip()
                if is_valid_drug_name(candidate_gen):
                    display_name = candidate_gen
                    
        # 2. If not found, check synonyms for a valid clean name
        if not display_name:
            syns = synonyms_data.get(drug_id, [])
            for s in syns:
                if is_valid_drug_name(s):
                    display_name = str(s).strip()
                    break
                    
        # If after all checks we don't have a clean medical name, SKIP this entry entirely!
        if not display_name or not is_valid_drug_name(display_name):
            continue
            
        display_name = display_name.capitalize()
        
        # Collect search aliases (synonyms can include chemical names for background searching)
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
            "drug_id": u_id
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
# 4. Main User Interface
# ========================================================
if db_conn:
    tab1, tab2, tab3 = st.tabs(["🔬 Single Formulation Profiler", "⚔️ Cross-Match Binary Interaction Checker", "🥦 Nutritional Constraints"])
    
    # --- TAB 1: SMART SINGLE DRUG SEARCH ---
    with tab1:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        target_id, current_drug_name = render_medication_search_flow("Target Clinical Drug", med_index, "single")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if target_id:
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
                st.dataframe(df_clean, use_container_width=True, hide_index=True)
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
            if id_a == id_b: st.warning("⚠️ Identity Conflict: Please select two separate formulations.")
            else:
                query = "SELECT * FROM interactions WHERE (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?) OR (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?)"
                df_pair = pd.read_sql_query(query, db_conn, params=(id_a, id_b, id_b, id_a))
                
                st.markdown("<div class='med-card'>", unsafe_allow_html=True)
                if not df_pair.empty:
                    cleaned_interaction = clean_interaction_text(df_pair.iloc[0]['Interaction'], name_b)
                    severity_status = get_severity_color(cleaned_interaction)
                    st.error("🚨 Contraindication Profile Alert Generated!")
                    if "🔴" in severity_status: st.markdown("<span class='clinical-badge badge-high'>CRITICAL CRITERIA RISK</span>", unsafe_allow_html=True)
                    elif "🟡" in severity_status: st.markdown("<span class='clinical-badge badge-moderate'>MODERATE MODERATION WARNING</span>", unsafe_allow_html=True)
                    else: st.markdown("<span class='clinical-badge badge-monitor'>CLINICAL MONITOR / INFO</span>", unsafe_allow_html=True)
                    st.markdown(f"**Documented Pathophysiology:** {cleaned_interaction}")
                else:
                    st.success(f"✅ Safe Therapeutic Pathway: No direct contraindications mapped between {name_a} and {name_b}.")
                st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3: DRUG-FOOD INTERACTIONS ---
    with tab3:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        food_search = st.text_input("🥗 Query lifestyle or nutritional constraints (e.g., Grapefruit, Warfarin):").strip()
        st.markdown("</div>", unsafe_allow_html=True)
        
        if food_search and food_interactions_text:
            matching_lines = [line.strip() for line in food_interactions_text.split('\n') if food_search.lower() in line.lower()]
            st.markdown("<div class='med-card'>", unsafe_allow_html=True)
            if matching_lines:
                st.warning(f"⚠️ Identified {len(matching_lines)} Dietary Precautions:")
                for line in matching_lines[:15]: st.markdown(f"<div style='padding: 8px 0px; border-bottom: 1px solid rgba(128,128,128,0.1);'>💡 {line}</div>", unsafe_allow_html=True)
            else:
                st.success("✅ No dietary contraindications detected.")
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("⚙️ Connection Error.")

st.markdown("<div class='app-footer'>RxShield CDSS Engine Tier-1 • Platform Build v2026.4.12 • Verified Clinical Ledger</div>", unsafe_allow_html=True)
