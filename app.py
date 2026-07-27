import streamlit as st
import pandas as pd
import sqlite3
import requests
import zipfile
import os
import json

st.set_page_config(
    page_title="RxShield | Clinical Decision Support",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ RxShield | Advanced Clinical Decision Support")
st.write("Comprehensive platform for Drug-Drug and Drug-Food interactions.")

# ========================================================
# 1. Configuration & Database Initialization
# ========================================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mustafaamer97/RxShield/main"
ZIP_FILE_URL = f"{GITHUB_RAW_URL}/all_id_interaction.zip"
DB_ZIP_PATH = "all_id_interaction.zip"
DB_FILE_PATH = "all_id_interaction.db"

@st.cache_resource
def init_database():
    if not os.path.exists(DB_FILE_PATH):
        with st.spinner('⏳ Initializing database from GitHub (First time setup)...'):
            response = requests.get(ZIP_FILE_URL, stream=True)
            if response.status_code == 200:
                with open(DB_ZIP_PATH, 'wb') as f:
                    f.write(response.content)
                with zipfile.ZipFile(DB_ZIP_PATH, 'r') as zip_ref:
                    zip_ref.extractall(".")
                if os.path.exists(DB_ZIP_PATH):
                    os.remove(DB_ZIP_PATH)
            else:
                st.error("❌ Failed to download database.")
                return None
    return sqlite3.connect(DB_FILE_PATH, check_same_thread=False)

db_conn = init_database()

# ========================================================
# 2. Loading Companion JSON & Text Files
# ========================================================
@st.cache_data
def load_helper_data():
    synonyms = {}
    food_data = ""
    
    # Load Synonyms
    if os.path.exists('drugs_synonyms.json'):
        with open('drugs_synonyms.json', 'r', encoding='utf-8') as f:
            synonyms = json.load(f)
            
    # Load Food Interactions Text File
    food_file_name = 'Drug to Food interactions ...'
    if os.path.exists(food_file_name):
        with open(food_file_name, 'r', encoding='utf-8') as f:
            food_data = f.read()
            
    return synonyms, food_data

synonyms_dict, food_interactions_text = load_helper_data()

# Helper function to get Drug ID from name
def get_drug_id(name_query):
    name_query = name_query.strip().lower()
    if not name_query:
        return None
    # If it's already a DB ID, return it directly
    if name_query.startswith("db") and len(name_query) > 2:
        return name_query.upper()
    # Search in synonyms dictionary
    for drug_id, syn_list in synonyms_dict.items():
        if any(name_query in str(syn).lower() for syn in syn_list):
            return drug_id.upper()
    return None

# ========================================================
# 3. Main Interactive Tabs
# ========================================================
if db_conn:
    tab1, tab2, tab3 = st.tabs([
        "🔍 Single Drug Search (by Name/ID)", 
        "⚔️ Drug vs Drug Checker", 
        "🥦 Drug-Food Interactions"
    ])
    
    # --- TAB 1: SINGLE DRUG SEARCH ---
    with tab1:
        st.subheader("Search All Interactions for a Drug")
        drug_input = st.text_input("Enter Drug Name or ID (e.g., Aspirin, Paracetamol, DB04920):", key="single_search").strip()
        
        if drug_input:
            target_id = get_drug_id(drug_input)
            if target_id:
                st.info(f"🎯 Mapped '{drug_input}' to ID: **{target_id}**")
                query = "SELECT * FROM interactions WHERE \"Drug1 ID\" = ? OR \"Drug2 ID\" = ?"
                df_res = pd.read_sql_query(query, db_conn, params=(target_id, target_id))
                
                if not df_res.empty:
                    st.metric("Total Clinical Interactions", len(df_res))
                    st.dataframe(df_res, use_container_width=True)
                else:
                    st.warning(f"No clinical interactions found for {target_id}.")
            else:
                st.error(f"Could not find any registered drug matching '{drug_input}'.")

    # --- TAB 2: DRUG VS DRUG CHECKER ---
    with tab2:
        st.subheader("Check Interaction Between Two Specific Drugs")
        col1, col2 = st.columns(2)
        with col1:
            drug_a = st.text_input("Enter First Drug:", placeholder="e.g., Aspirin", key="drug_a").strip()
        with col2:
            drug_b = st.text_input("Enter Second Drug:", placeholder="e.g., Warfarin", key="drug_b").strip()
            
        if drug_a and drug_b:
            id_a = get_drug_id(drug_a)
            id_b = get_drug_id(drug_b)
            
            if id_a and id_b:
                st.info(f"Searching connection between **{id_a}** and **{id_b}**...")
                query = """
                SELECT * FROM interactions 
                WHERE (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?) 
                   OR (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?)
                """
                df_pair = pd.read_sql_query(query, db_conn, params=(id_a, id_b, id_b, id_a))
                
                if not df_pair.empty:
                    st.error("⚠️ Clinical Interaction Detected!")
                    for idx, row in df_pair.iterrows():
                        st.markdown(f"**Description:** {row['Interaction']}")
                else:
                    st.success("✅ Safe! No direct interaction found between these two drugs in the database.")
            else:
                st.error("Make sure both drug names are spelled correctly.")

    # --- TAB 3: DRUG-FOOD INTERACTIONS ---
    with tab3:
        st.subheader("Dietary & Food Warnings")
        food_search = st.text_input("Search food warnings for a drug:", placeholder="e.g., Alcohol, Grapefruit").strip()
        
        if food_search and food_interactions_text:
            # Simple text filtering for lines containing the keyword
            matching_lines = [line for line in food_interactions_text.split('\n') if food_search.lower() in line.lower()]
            if matching_lines:
                st.warning(f"Found {len(matching_lines)} dietary warnings:")
                for line in matching_lines[:15]: # Show top 15 matches
                    st.write(f"• {line}")
            else:
                st.success("No specific food/dietary interaction matched your search.")
        elif not food_interactions_text:
            st.info("Food interaction file not loaded or empty.")
        else:
            st.info("Type a drug or food component name above to display global warnings.")

else:
    st.error("⚙️ Connection error.")
