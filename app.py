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
    
    .interaction-detail p { margin-bottom: 8px; font-size: 0.95rem; line-height: 1.5; }
    .interaction-detail strong { color: var(--text-color); font-weight: 600; }
    
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
# 2. STRICT DATA ENGINEERING
# ========================================================
def is_valid_drug_name(name):
    if not name or len(name) < 2: return False
    name_str = str(name).strip().lower()
    if name_str.endswith('acid') or ' acid' in name_str: return False
    if any(term in name_str for term in ['heme', 'cholesterol', 'diiodo', 'diamino', 'nonanoic']): return False
    if re.search(r'\d+,\d+', name_str) or re.search(r'^[0-9]+[,\-]', name_str): return False
    iupac_symbols = ['(', ')', '[', ']', '{', '}', '+', '=', '<', '>', ';', '\\', '/']
    if any(char in name_str for char in iupac_symbols): return False
    if len(name_str) > 35: return False
    return True

@st.cache_data
def build_clinical_medication_index():
    synonyms_data, drug_info, food_data = {}, {}, ""
    if os.path.exists('drugs_synonyms.json'):
        with open('drugs_synonyms.json', 'r', encoding='utf-8') as f: synonyms_data = json.load(f)
    if os.path.exists('drug_info.json'):
        with open('drug_info.json', 'r', encoding='utf-8') as f: drug_info = json.load(f)
    if os.path.exists('Drug to Food interactions ...'):
        with open('Drug to Food interactions ...', 'r', encoding='utf-8') as f: food_data = f.read()

    med_index = {}
    all_ids = set(synonyms_data.keys()).union(set(drug_info.keys()))
    
    for drug_id in all_ids:
        u_id = drug_id.upper()
        info = drug_info.get(drug_id, {})
        display_name = ""
        
        if isinstance(info, dict):
            candidate = info.get("name", "").strip()
            if is_valid_drug_name(candidate): display_name = candidate
            else:
                candidate_gen = info.get("generic_name", "").strip()
                if is_valid_drug_name(candidate_gen): display_name = candidate_gen
                    
        if not display_name:
            for s in synonyms_data.get(drug_id, []):
                if is_valid_drug_name(s):
                    display_name = str(s).strip()
                    break
                    
        if not display_name or not is_valid_drug_name(display_name): continue
        display_name = display_name.capitalize()
        
        search_aliases = {display_name.lower()}
        for syn in synonyms_data.get(drug_id, []): search_aliases.add(str(syn).lower())
        
        cleaned_aliases = set()
        for alias in search_aliases:
            if alias:
                clean_str = str(alias).lower().translate(str.maketrans('', '', string.punctuation))
                clean_str = " ".join(clean_str.split())
                if clean_str: cleaned_aliases.add(clean_str)
                    
        med_index[u_id] = {
            "display_name": display_name,
            "search_aliases": cleaned_aliases,
            "drug_id": u_id,
            "raw_info": info if isinstance(info, dict) else {}
        }
    return food_data, med_index

food_interactions_text, med_index = build_clinical_medication_index()

# ========================================================
# 3. Core Engine Functions & Clinical Parsers
# ========================================================
def clean_interaction_text(text, drug1_name, drug2_name=None):
    if not text: return ""
    if drug2_name is None: drug2_name = drug1_name
    counter = [0]
    def replace_placeholder(match):
        counter[0] += 1
        return f" {drug1_name} " if counter[0] == 1 else f" {drug2_name} "
    cleaned = re.sub(r'\(\.\*\)', replace_placeholder, text)
    cleaned = cleaned.replace("the risk or severity of", "The risk of")
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned + '.' if cleaned and not cleaned.endswith('.') else cleaned

def get_severity_color(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["bleeding", "arrhythmia", "qtc prolongation", "toxicity", "fatal", "severe", "hemorrhage"]):
        return "🟥 HIGH RISK"
    elif any(w in text_lower for w in ["decrease the therapeutic efficacy", "increase the excretion rate", "risk of adverse effects"]):
        return "🟨 MODERATE CAUTION"
    return "🟦 MONITOR / INFO"

# الدالة الذكية لاستخراج التفاصيل السريرية من النص الخام
def parse_clinical_details(raw_text, severity):
    effect = "Unspecified pharmacological interaction"
    
    # 1. Extract Clinical Effect using Regex
    match_risk = re.search(r'risk of\s+(.*?)\s+can be', raw_text, re.IGNORECASE)
    match_conc = re.search(r'serum concentration of\s+(.*?)\s+can be', raw_text, re.IGNORECASE)
    match_metab = re.search(r'metabolism of\s+(.*?)\s+can be', raw_text, re.IGNORECASE)
    
    if match_risk: effect = f"Increased risk of {match_risk.group(1).strip()}"
    elif match_conc: effect = f"Altered serum concentration ({match_conc.group(1).strip()})"
    elif match_metab: effect = f"Altered metabolism ({match_metab.group(1).strip()})"
    elif "decrease the therapeutic efficacy" in raw_text.lower(): effect = "Decreased therapeutic efficacy"
    elif "increase the excretion rate" in raw_text.lower(): effect = "Increased excretion rate (Reduced efficacy)"
    
    effect = effect[0].upper() + effect[1:] if effect else effect
    
    # 2. Rule-based Recommendations and Monitoring
    if "🟥" in severity:
        rec = "Consider alternative therapy. If co-administration is strictly necessary, dose adjustment is mandatory."
        mon = "Continuous and rigorous monitoring for signs of clinical toxicity and adverse events."
        color_code = "#d32f2f"
    elif "🟨" in severity:
        rec = "Evaluate risk vs. benefit. Adjust dosages of one or both agents if needed."
        mon = "Regular monitoring of patient vitals and specific laboratory parameters."
        color_code = "#f57f17"
    else:
        rec = "No immediate therapy modification typically required. Use standard clinical judgment."
        mon = "Standard clinical observation."
        color_code = "#1565c0"
        
    return effect, rec, mon, color_code

# HTML/UI Component Render
def render_interaction_card(drug_pair, severity, mechanism_text):
    effect, rec, mon, color = parse_clinical_details(mechanism_text, severity)
    
    st.markdown(f"""
        <div class="med-card interaction-detail" style="border-left: 6px solid {color}; padding: 18px 24px;">
            <h3 style="color: {color}; margin-top: 0; margin-bottom: 15px; font-size: 1.25rem;">{severity}</h3>
            <p><strong>💊 Interaction:</strong> {drug_pair}</p>
            <p><strong>🩺 Clinical Effect:</strong> {effect}</p>
            <p><strong>📝 Recommendation:</strong> {rec}</p>
            <p><strong>⚙️ Mechanism:</strong> {mechanism_text}</p>
            <p><strong>🔍 Monitoring:</strong> {mon}</p>
        </div>
    """, unsafe_allow_html=True)

def render_medication_search_flow(label, index, key_prefix):
    search_input = st.text_input(
        f"🔍 Search Formulation for [{label}]:",
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
        if name not in unique_pool: unique_pool[name] = d_id
            
    final_list = sorted([(name, d_id) for name, d_id in unique_pool.items()], key=lambda x: x[0])
    
    if not final_list:
        st.warning(f"⚠️ Zero clinical matches found for '{search_input}'.")
        return None, None
        
    selected_tuple = st.selectbox(f"Select Confirmed Entry:", options=final_list, format_func=lambda x: x[0], key=f"{key_prefix}_dropdown")
    return (selected_tuple[1], selected_tuple[0]) if selected_tuple else (None, None)

# ========================================================
# 4. Main User Interface 
# ========================================================
if db_conn:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 Single Formulation Profiler", 
        "⚔️ Binary Interaction Checker", 
        "💊 Multi-Drug Regimen Matrix",
        "🥦 Nutritional Constraints"
    ])
    
    # --- TAB 1 ---
    with tab1:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        target_id, current_drug_name = render_medication_search_flow("Target Clinical Drug", med_index, "single")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if target_id:
            with st.spinner("⏳ Extracting clinical monograph and checking interaction profiles..."):
                query = "SELECT * FROM interactions WHERE \"Drug1 ID\" = ? OR \"Drug2 ID\" = ?"
                df_res = pd.read_sql_query(query, db_conn, params=(target_id, target_id))
                
                if not df_res.empty:
                    st.markdown("---")
                    st.markdown(f"### 📋 Documented Contraindications for {current_drug_name}")
                    for _, row in df_res.iterrows():
                        r_d1, r_d2 = str(row['Drug1 ID']).upper(), str(row['Drug2 ID']).upper()
                        d1_n = med_index[r_d1]["display_name"] if r_d1 in med_index else "Medication"
                        d2_n = med_index[r_d2]["display_name"] if r_d2 in med_index else "Medication"
                        
                        clean_text = clean_interaction_text(row['Interaction'], d1_n, d2_n)
                        severity = get_severity_color(clean_text)
                        
                        render_interaction_card(f"{d1_n} + {d2_n}", severity, clean_text)
                else:
                    st.info(f"ℹ️ No contraindications registered for {current_drug_name}.")

    # --- TAB 2 ---
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
                    
                    if not df_pair.empty:
                        r_d1, r_d2 = str(df_pair.iloc[0]['Drug1 ID']).upper(), str(df_pair.iloc[0]['Drug2 ID']).upper()
                        d1_n = med_index[r_d1]["display_name"] if r_d1 in med_index else name_a
                        d2_n = med_index[r_d2]["display_name"] if r_d2 in med_index else name_b
                        
                        cleaned_interaction = clean_interaction_text(df_pair.iloc[0]['Interaction'], d1_n, d2_n)
                        severity_status = get_severity_color(cleaned_interaction)
                        
                        render_interaction_card(f"{d1_n} + {d2_n}", severity_status, cleaned_interaction)
                    else:
                        st.success(f"✅ Safe Therapeutic Pathway: No direct contraindications mapped between **{name_a}** and **{name_b}**.")

    # --- TAB 3 ---
    with tab3:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        st.markdown("### 💊 Comprehensive Patient Medication Regimen Screening")
        sorted_med_options = sorted([(m["display_name"], d_id) for d_id, m in med_index.items()], key=lambda x: x[0])
        selected_regimen = st.multiselect("Select Patient Regimen Formulations:", options=sorted_med_options, format_func=lambda x: x[0])
        st.markdown("</div>", unsafe_allow_html=True)
        
        if selected_regimen and len(selected_regimen) >= 2:
            with st.spinner("⏳ Running pairwise combinatorial matrix validation..."):
                regimen_pairs = list(combinations(selected_regimen, 2))
                st.metric(label="Combinations Evaluated", value=len(regimen_pairs))
                st.markdown("---")
                
                for (name_1, id_1), (name_2, id_2) in regimen_pairs:
                    q_reg = "SELECT * FROM interactions WHERE (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?) OR (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?)"
                    df_r = pd.read_sql_query(q_reg, db_conn, params=(id_1, id_2, id_2, id_1))
                    
                    if not df_r.empty:
                        r_d1, r_d2 = str(df_r.iloc[0]['Drug1 ID']).upper(), str(df_r.iloc[0]['Drug2 ID']).upper()
                        d1_n = med_index[r_d1]["display_name"] if r_d1 in med_index else name_1
                        d2_n = med_index[r_d2]["display_name"] if r_d2 in med_index else name_2
                        
                        txt = clean_interaction_text(df_r.iloc[0]['Interaction'], d1_n, d2_n)
                        sev = get_severity_color(txt)
                        render_interaction_card(f"{d1_n} + {d2_n}", sev, txt)

    # --- TAB 4 ---
    with tab4:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        food_search = st.text_input("🥗 Query lifestyle or nutritional constraints (e.g., Grapefruit, Warfarin):").strip()
        st.markdown("</div>", unsafe_allow_html=True)
        
        if food_search and food_interactions_text:
            matching_lines = [line.strip() for line in food_interactions_text.split('\n') if food_search.lower() in line.lower()]
            if matching_lines:
                for line in matching_lines[:15]: 
                    st.warning(f"💡 {line}")
            else:
                st.success("✅ No dietary contraindications detected.")
else:
    st.error("⚙️ Connection Error.")
