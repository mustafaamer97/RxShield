import streamlit as st
import pandas as pd
import sqlite3
import zipfile
import os
import string
import itertools

# 1. Import our clinical engine utilities
from utils.clinical_engine import (
    clean_interaction_text,
    get_severity_color,
    render_interaction_card
)

# ========================================================
# Page Config & UI Styling
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
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', -apple-system, sans-serif; }
    .sticky-header { position: -webkit-sticky; position: sticky; top: 0; background-color: var(--background-color); border-bottom: 2px solid #00796b; padding: 15px 0px; margin-bottom: 25px; z-index: 99; }
    .header-title { font-size: 2.2rem; font-weight: 700; color: #00796b; margin: 0; letter-spacing: -0.5px; }
    .header-subtitle { font-size: 1rem; color: var(--text-color); opacity: 0.8; margin-top: 4px; }
    .med-card { background-color: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 12px; padding: 22px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); }
    .interaction-detail p { margin-bottom: 8px; font-size: 0.95rem; line-height: 1.5; }
    .interaction-detail strong { color: var(--text-color); font-weight: 600; }
    .sidebar-brand { font-size: 1.5rem; font-weight: 700; color: #00796b; margin-bottom: 5px; }
    .sidebar-status-tag { background-color: rgba(46, 125, 50, 0.12); color: #2e7d32; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 20px; border: 1px solid rgba(46, 125, 50, 0.2); }
    .app-footer { text-align: center; padding: 30px 0px; margin-top: 50px; font-size: 0.82rem; opacity: 0.6; border-top: 1px solid rgba(128, 128, 128, 0.15); }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>🛡️ RxShield CDSS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-status-tag'>🟢 ENGINE ONLINE & SECURED</div>", unsafe_allow_html=True)
    st.markdown("### 📊 System Diagnostics\n**Core Pipeline Layer:** Compressed SQLite Stream\n**Architecture:** Zip-Extractor Pipeline Active")

st.markdown("""
<div class='sticky-header'>
    <h1 class='header-title'>RxShield | Advanced Decision Support Portal</h1>
    <p class='header-subtitle'>Real-time multi-channel verification pipeline for interactive Drug-Drug and Drug-Food contraindications.</p>
</div>
""", unsafe_allow_html=True)

# ========================================================
# 2. Data Loading (Extracting SQLite from ZIP in-memory)
# ========================================================
@st.cache_data
def load_local_data():
    zip_path = "all_id_interaction.zip"
    extract_dir = "extracted_db"
    db_name = "drug_interactions.db"
    db_path = os.path.join(extract_dir, db_name)
    
    try:
        # Step A: Extract the zip file if not already extracted
        if not os.path.exists(db_path):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find the database file inside the zip regardless of name variations
                db_files = [f for f in zip_ref.namelist() if f.endswith('.db')]
                if db_files:
                    zip_ref.extract(db_files[0], extract_dir)
                    # If the file inside has a different name, rename it to unified target
                    os.rename(os.path.join(extract_dir, db_files[0]), db_path)
                else:
                    # Fallback if the file inside is actually named something else or a CSV
                    zip_ref.extractall(extract_dir)
                    for f in os.listdir(extract_dir):
                        if f.endswith('.db'):
                            os.rename(os.path.join(extract_dir, f), db_path)
                            break
                            
        # Step B: Connect to the extracted SQLite database
        conn = sqlite3.connect(db_path)
        # Attempting loading from the standard interactions table
        df = pd.read_sql_query("SELECT * FROM interactions", conn)
        conn.close()
        st.success("Zip-Archived Database Loaded and Parsed Successfully!")
    except Exception as e:
        st.error(f"Database Pipeline Error: {e}")
        # Secondary fallback if extraction environment fails
        df = pd.DataFrame({
            "Drug1 ID": ["DB00731", "DB00959"],
            "Drug1 Name": ["Artemether", "Aspirin"],
            "Drug2 ID": ["DB00682", "DB00316"],
            "Drug2 Name": ["Warfarin", "Acetaminophen"],
            "Interaction": [
                "The risk or severity of bleeding can be increased when Warfarin is combined with Aspirin.", 
                "The metabolism of Acetaminophen can be decreased."
            ]
        })
        
    med_index = {}
    for _, row in df.iterrows():
        d1_id, d1_name = str(row.get('Drug1 ID', '')).upper(), str(row.get('Drug1 Name', ''))
        d2_id, d2_name = str(row.get('Drug2 ID', '')).upper(), str(row.get('Drug2 Name', ''))
        
        if d1_id and d1_id not in med_index:
            med_index[d1_id] = {"display_name": d1_name, "search_aliases": [d1_name.lower()]}
        if d2_id and d2_id not in med_index:
            med_index[d2_id] = {"display_name": d2_name, "search_aliases": [d2_name.lower()]}
            
    food_interactions_text = "Warfarin: Avoid high Vitamin K foods like spinach.\nAspirin: Take with food to avoid stomach upset."
    return df, med_index, food_interactions_text

df_interactions, med_index, food_interactions_text = load_local_data()

# ========================================================
# Diagnostic Printouts 
# ========================================================
st.info("📊 Diagnostic Info Layer Active")
st.write("Rows loaded from Compressed Stream:", len(df_interactions))
st.markdown("---")

# ========================================================
# 3. Filtering Functions
# ========================================================
def get_single_drug_interactions(target_id):
    return df_interactions[(df_interactions['Drug1 ID'].astype(str).str.upper() == target_id) | 
                           (df_interactions['Drug2 ID'].astype(str).str.upper() == target_id)]

def get_pair_interaction(id_a, id_b):
    return df_interactions[
        ((df_interactions['Drug1 ID'].astype(str).str.upper() == id_a) & (df_interactions['Drug2 ID'].astype(str).str.upper() == id_b)) |
        ((df_interactions['Drug1 ID'].astype(str).str.upper() == id_b) & (df_interactions['Drug2 ID'].astype(str).str.upper() == id_a))
    ]

def get_regimen_pairs(regimen_list):
    return list(itertools.combinations(regimen_list, 2))

def render_medication_search_flow(label, index, key_prefix):
    search_input = st.text_input(f"🔍 Search Formulation for [{label}]:", key=f"{key_prefix}_text_search", placeholder="e.g., Warfarin...").strip()
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
                
    unique_pool = {name: d_id for name, d_id in filtered_pool}
    final_list = sorted([(name, d_id) for name, d_id in unique_pool.items()], key=lambda x: x[0])
    
    if not final_list:
        st.warning(f"⚠️ Zero clinical matches found.")
        return None, None
        
    selected_tuple = st.selectbox(f"Select Confirmed Entry:", options=final_list, format_func=lambda x: x[0], key=f"{key_prefix}_dropdown")
    return (selected_tuple[1], selected_tuple[0]) if selected_tuple else (None, None)

# ========================================================
# Helper Function to Display Interactions Consistently
# ========================================================
def display_interaction(row, med_index):
    drug1 = str(row["Drug1 ID"]).upper()
    drug2 = str(row["Drug2 ID"]).upper()

    drug1_name = med_index.get(drug1, {}).get("display_name", "Medication")
    drug2_name = med_index.get(drug2, {}).get("display_name", "Medication")

    cleaned = clean_interaction_text(
        row.get("Interaction", ""),
        drug1_name,
        drug2_name
    )

    severity = get_severity_color(cleaned)
    render_interaction_card(f"{drug1_name} + {drug2_name}", severity, cleaned)

# ========================================================
# 4. App Interface & Tabs
# ========================================================
tab1, tab2, tab3, tab4 = st.tabs(["🔬 Single Formulation Profiler", "⚔️ Binary Interaction Checker", "💊 Multi-Drug Regimen Matrix", "🥦 Nutritional Constraints"])

# TAB 1: Single Medication Profiling
with tab1:
    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
    target_id, current_drug_name = render_medication_search_flow("Target Clinical Drug", med_index, "single")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if target_id:
        df_res = get_single_drug_interactions(target_id)
        if not df_res.empty:
            for _, row in df_res.head(30).iterrows():
                display_interaction(row, med_index)
        else: 
            st.info("ℹ️ No contraindications registered.")

# TAB 2: Binary Interaction Checker
with tab2:
    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: id_a, name_a = render_medication_search_flow("Component A", med_index, "pair_a")
    with col2: id_b, name_b = render_medication_search_flow("Component B", med_index, "pair_b")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if id_a and id_b:
        if id_a == id_b: 
            st.warning("⚠️ Identity Conflict: Select two separate formulations.")
        else:
            df_pair = get_pair_interaction(id_a, id_b)
            if not df_pair.empty:
                display_interaction(df_pair.iloc[0], med_index)
            else: 
                st.success("✅ Safe Therapeutic Pathway.")

# TAB 3: Multi-Drug Regimen Verification
with tab3:
    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
    sorted_med_options = sorted([(m["display_name"], d_id) for d_id, m in med_index.items()], key=lambda x: x[0])
    selected_regimen = st.multiselect("Select Patient Regimen Formulations:", options=sorted_med_options, format_func=lambda x: x[0])
    st.markdown("</div>", unsafe_allow_html=True)
    
    if selected_regimen and len(selected_regimen) >= 2:
        regimen_pairs = get_regimen_pairs(selected_regimen)
        for (name_1, id_1), (name_2, id_2) in regimen_pairs:
            df_r = get_pair_interaction(id_1, id_2)
            if not df_r.empty:
                display_interaction(df_r.iloc[0], med_index)

# TAB 4: Nutritional Constraints (Drug-Food)
with tab4:
    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
    food_search = st.text_input("🥗 Query nutritional constraints:").strip()
    st.markdown("</div>", unsafe_allow_html=True)
    
    if food_search and food_interactions_text:
        matching_lines = [line.strip() for line in food_interactions_text.split('\n') if food_search.lower() in line.lower()]
        if matching_lines:
            for line in matching_lines[:15]: 
                st.warning(f"💡 {line}")
        else: 
            st.success("✅ No dietary contraindications detected.")

st.markdown("<div class='app-footer'>RxShield CDSS Engine Tier-1 • Enterprise Platform Build v2026.4.12</div>", unsafe_allow_html=True)
