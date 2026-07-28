import streamlit as st
import pandas as pd
import string

# Import external core utility layers
from utils.db_manager import init_database
from utils.data_loader import build_clinical_medication_index
from utils.clinical_engine import clean_interaction_text, get_severity_color, render_interaction_card

# Import newly decoupled service layer functions
from services.interaction_service import (
    get_single_drug_interactions,
    get_pair_interaction,
    get_regimen_pairs
)

# ========================================================
# Page Config & Enterprise Medical UI Styling
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

# Sidebar UI Section
with st.sidebar:
    st.markdown("<div class='sidebar-brand'>🛡️ RxShield CDSS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-status-tag'>🟢 ENGINE ONLINE & SECURED</div>", unsafe_allow_html=True)
    st.markdown("### 📊 System Diagnostics\n**Core Pipeline Layer:** Modular Clinical Verification Instance\n**Architecture:** Service Layer Pattern Active")

st.markdown("""
<div class='sticky-header'>
    <h1 class='header-title'>RxShield | Advanced Decision Support Portal</h1>
    <p class='header-subtitle'>Real-time multi-channel verification pipeline for interactive Drug-Drug and Drug-Food contraindications.</p>
</div>
""", unsafe_allow_html=True)

# Initialize database connections and indices from external utilities
db_conn = init_database()
food_interactions_text, med_index = build_clinical_medication_index()

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
            if any(normalized_query in alias for alias in metadata["search_aliases"]): filtered_pool.append((metadata["display_name"], d_id))
    unique_pool = {name: d_id for name, d_id in filtered_pool}
    final_list = sorted([(name, d_id) for name, d_id in unique_pool.items()], key=lambda x: x[0])
    if not final_list:
        st.warning(f"⚠️ Zero clinical matches found.")
        return None, None
    selected_tuple = st.selectbox(f"Select Confirmed Entry:", options=final_list, format_func=lambda x: x[0], key=f"{key_prefix}_dropdown")
    return (selected_tuple[1], selected_tuple[0]) if selected_tuple else (None, None)

if db_conn:
    tab1, tab2, tab3, tab4 = st.tabs(["🔬 Single Formulation Profiler", "⚔️ Binary Interaction Checker", "💊 Multi-Drug Regimen Matrix", "🥦 Nutritional Constraints"])
    
    # TAB 1: Single Medication Profiling
    with tab1:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        target_id, current_drug_name = render_medication_search_flow("Target Clinical Drug", med_index, "single")
        st.markdown("</div>", unsafe_allow_html=True)
        if target_id:
            # Querying via decoupled service layer function
            df_res = get_single_drug_interactions(db_conn, target_id)
            
            if not df_res.empty:
                for _, row in df_res.iterrows():
                    r_d1, r_d2 = str(row['Drug1 ID']).upper(), str(row['Drug2 ID']).upper()
                    d1_n = med_index[r_d1]["display_name"] if r_d1 in med_index else "Medication"
                    d2_n = med_index[r_d2]["display_name"] if r_d2 in med_index else "Medication"
                    clean_text = clean_interaction_text(row['Interaction'], d1_n, d2_n)
                    render_interaction_card(f"{d1_n} + {d2_n}", get_severity_color(clean_text), clean_text)
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
                # Utilizing decoupled binary interaction service
                df_pair = get_pair_interaction(db_conn, id_a, id_b)
                
                if not df_pair.empty:
                    r_d1, r_d2 = str(df_pair.iloc[0]['Drug1 ID']).upper(), str(df_pair.iloc[0]['Drug2 ID']).upper()
                    d1_n = med_index[r_d1]["display_name"] if r_d1 in med_index else name_a
                    d2_n = med_index[r_d2]["display_name"] if r_d2 in med_index else name_b
                    txt = clean_interaction_text(df_pair.iloc[0]['Interaction'], d1_n, d2_n)
                    render_interaction_card(f"{d1_n} + {d2_n}", get_severity_color(txt), txt)
                else: 
                    st.success("✅ Safe Therapeutic Pathway.")

    # TAB 3: Multi-Drug Regimen Verification
    with tab3:
        st.markdown("<div class='med-card'>", unsafe_allow_html=True)
        sorted_med_options = sorted([(m["display_name"], d_id) for d_id, m in med_index.items()], key=lambda x: x[0])
        selected_regimen = st.multiselect("Select Patient Regimen Formulations:", options=sorted_med_options, format_func=lambda x: x[0])
        st.markdown("</div>", unsafe_allow_html=True)
        if selected_regimen and len(selected_regimen) >= 2:
            
            # Extract combined pairs via the regimen service layer
            regimen_pairs = get_regimen_pairs(selected_regimen)
            
            for (name_1, id_1), (name_2, id_2) in regimen_pairs:
                # Re-use the decoupled pair interaction function loop for unified logic
                df_r = get_pair_interaction(db_conn, id_1, id_2)
                
                if not df_r.empty:
                    r_d1, r_d2 = str(df_r.iloc[0]['Drug1 ID']).upper(), str(df_r.iloc[0]['Drug2 ID']).upper()
                    d1_n = med_index[r_d1]["display_name"] if r_d1 in med_index else name_1
                    d2_n = med_index[r_d2]["display_name"] if r_d2 in med_index else name_2
                    txt = clean_interaction_text(df_r.iloc[0]['Interaction'], d1_n, d2_n)
                    render_interaction_card(f"{d1_n} + {d2_n}", get_severity_color(txt), txt)

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
else:
    st.error("⚙️ Connection Error: Database connection could not be established.")

st.markdown("<div class='app-footer'>RxShield CDSS Engine Tier-1 • Enterprise Platform Build v2026.4.12</div>", unsafe_allow_html=True)
