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

st.title("🛡️ RxShield | Drug Interaction Checker")

# ========================================================
# 1. GitHub Repository Storage Configuration
# ========================================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mustafaamer97/RxShield/main"
ZIP_FILE_URL = f"{GITHUB_RAW_URL}/all_id_interaction.zip"

DB_ZIP_PATH = "all_id_interaction.zip"
DB_FILE_PATH = "all_id_interaction.db"

# ========================================================
# 2. Database Downloader & Extractor Function
# ========================================================
@st.cache_resource
def init_database():
    # If the database file doesn't exist locally, download and unzip it
    if not os.path.exists(DB_FILE_PATH):
        with st.spinner('⏳ Initializing large database from GitHub (This happens only once)...'):
            # Download the zip file
            response = requests.get(ZIP_FILE_URL, stream=True)
            if response.status_code == 200:
                with open(DB_ZIP_PATH, 'wb') as f:
                    f.write(response.content)
                
                # Extract the zip file
                with zipfile.ZipFile(DB_ZIP_PATH, 'r') as zip_ref:
                    zip_ref.extractall(".")
                
                # Clean up the zip file to save space
                if os.path.exists(DB_ZIP_PATH):
                    os.remove(DB_ZIP_PATH)
            else:
                st.error("❌ Failed to download the database from GitHub. Please check if the file exists in your repository.")
                return None
    
    # Connect to the SQLite database
    conn = sqlite3.connect(DB_FILE_PATH, check_same_thread=False)
    return conn

# ========================================================
# 3. RxShield Search Engine Class
# ========================================================
class RxShieldEngine:
    def __init__(self):
        self.drug_info = {}
        self.synonyms = {}

    def load_json_data(self):
        # Load companion JSON files if they exist in the repository
        if os.path.exists('drug_info.json'):
            with open('drug_info.json', 'r', encoding='utf-8') as f:
                self.drug_info = json.load(f)
        
        if os.path.exists('drugs_synonyms.json'):
            with open('drugs_synonyms.json', 'r', encoding='utf-8') as f:
                self.synonyms = json.load(f)

# Initialize the engine
engine = RxShieldEngine()
engine.load_json_data()

# Initialize connection to the SQLite database
db_conn = init_database()

if db_conn:
    st.success("🎉 Application started and connected to database successfully!")
    
    # Try to fetch a preview sample from the database
    try:
        # Assuming the table name inside the DB is 'all_id_interaction'
        df_sample = pd.read_sql_query("SELECT * FROM all_id_interaction LIMIT 5;", db_conn)
        
        st.write("### 📊 Database Preview Sample:")
        st.dataframe(df_sample)
    except Exception as e:
        st.warning(f"⚠️ Connected to DB, but failed to read table (Table name might be different): {e}")
else:
    st.error("⚙️ Something went wrong while initializing the database connection.")


