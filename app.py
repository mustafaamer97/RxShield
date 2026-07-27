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
st.write("Enter drug IDs or names to check for clinical interactions instantly.")

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
    
    conn = sqlite3.connect(DB_FILE_PATH, check_same_thread=False)
    return conn

db_conn = init_database()

# ========================================================
# 3. Interactive Search Section
# ========================================================
if db_conn:
    st.success("🎉 Database connected and protected by RxShield Engine.")
    
    # واجهة البحث
    st.write("---")
    st.subheader("🔍 Check Drug Interactions")
    
    search_query = st.text_input("Enter Drug ID (e.g., DB04920, DB01336):", "").strip()
    
    if search_query:
        with st.spinner('Searching database...'):
            try:
                # استعلام ذكي للبحث عن الدواء سواء كان في خانة Drug1 أو Drug2
                # قمنا بتثبيت اسم الجدول المكتشف 'interactions'
                query = """
                SELECT * FROM interactions 
                WHERE "Drug1 ID" LIKE ? OR "Drug2 ID" LIKE ?
                """
                df_result = pd.read_sql_query(query, db_conn, params=(f'%{search_query}%', f'%{search_query}%'))
                
                if not df_result.empty:
                    st.metric(label="Interactions Found", value=len(df_result))
                    st.dataframe(df_result, use_container_width=True)
                else:
                    st.warning(f"No interactions found for '{search_query}'.")
            except Exception as e:
                st.error(f"Search error: {e}")
                st.info("Tip: If column names differ, you can view the schema below.")
                
    # قسم جانبي اختياري لعرض عينة للتأكد من أسماء الأعمدة
    with st.expander("📊 Show Database Sample & Columns"):
        try:
            df_sample = pd.read_sql_query("SELECT * FROM interactions LIMIT 3;", db_conn)
            st.dataframe(df_sample)
        except:
            pass
else:
    st.error("⚙️ Connection error.")

