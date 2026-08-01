import streamlit as st
import json
import zipfile
import pandas as pd
import sqlite3
from pathlib import Path
from database.db import get_connection
from database.loader import NAME_TO_ID, ID_TO_NAME
from database.db import get_interaction

st.set_page_config(page_title="RxShield")

# --- Temporary SQLite Database (data_final_v5) Structural Check ---
try:
    st.subheader("🔍 Temporary SQLite (v5) Structural Check")
    ZIP_V5 = Path("data_final_v5.zip")
    DB_V5 = Path("data_final_v5.db")

    if not DB_V5.exists():
        with zipfile.ZipFile(ZIP_V5, "r") as z:
            z.extractall(".")

    conn_v5 = sqlite3.connect(DB_V5)
    conn_v5.row_factory = sqlite3.Row

    # Fetch all table names from the database schema
    tables_v5 = conn_v5.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    st.write("Tables Found:", [t["name"] for t in tables_v5])

    if tables_v5:
        target_table = tables_v5[0]["name"]
        st.write(f"Previewing top 5 rows from table: `{target_table}`")
        
        # Fetch and display the first 5 records
        rows_v5 = conn_v5.execute(f"SELECT * FROM `{target_table}` LIMIT 5;").fetchall()
        for r in rows_v5:
            st.write(dict(r))
    else:
        st.warning("No tables discovered in this database file.")

    conn_v5.close()
    st.markdown("---")
except Exception as db_err:
    st.error(f"Temporary DB v5 Load Error: {str(db_err)}")
    st.markdown("---")


# --- Temporary ZIP/CSV Structural Check Section ---
try:
    st.subheader("🔍 Temporary ZIP/CSV Structural Check")
    with zipfile.ZipFile("data_final_v5.zip", "r") as z:
        st.write("Files in ZIP:", z.namelist())
        
        csv_name = z.namelist()[0]
        with z.open(csv_name) as f:
            df = pd.read_csv(f)
            
    st.write("DataFrame Head Preview:")
    st.write(df.head())
    
    st.write("Columns List:")
    st.write(df.columns.tolist())
    st.markdown("---")
except Exception as zip_err:
    st.error(f"Temporary ZIP/CSV Load Error: {str(zip_err)}")
    st.markdown("---")


# --- Temporary JSON Debug Section ---
try:
    with open("drugs_synonyms.json", "r", encoding="utf-8") as f:
        debug_data = json.load(f)
    
    st.subheader("🔍 Temporary JSON Structural Check")
    st.write(next(iter(debug_data.items())))
    st.markdown("---")
except Exception as json_err:
    st.error(f"Temporary JSON Load Error: {str(json_err)}")
    st.markdown("---")


# --- Main Application: Drug–Drug Interaction Checker ---
st.header("🛡️ Drug–Drug Interaction Checker")

drug_names = sorted(NAME_TO_ID.keys())

col1, col2 = st.columns(2)

with col1:
    drug1 = st.selectbox("Drug 1", drug_names, index=None, placeholder="Select first drug")

with col2:
    drug2 = st.selectbox("Drug 2", drug_names, index=None, placeholder="Select second drug")

if st.button("Check Interaction", use_container_width=True):
    if drug1 and drug2:
        drug1_id = NAME_TO_ID[drug1]
        drug2_id = NAME_TO_ID[drug2]
        
        result = get_interaction(drug1_id, drug2_id)

        if result:
            st.success("Interaction Found ✅")
            try:
                st.write(dict(result))
            except (TypeError, ValueError):
                st.write(list(result))
        else:
            st.info("No interaction found.")
    else:
        st.warning("⚠️ Please select both drugs to perform the check.")

st.markdown("---")


# --- System Diagnostics: Database Integrity Verification ---
try:
    conn = get_connection()
    
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchone()

    if table:
        try:
            table_name = table["name"]
        except (TypeError, IndexError):
            table_name = table[0]

        st.caption(f"⚡ Connected to system database table: `{table_name}`")
        
        count = conn.execute(
            f"SELECT COUNT(*) FROM `{table_name}`;"
        ).fetchone()[0]
        st.caption(f"📊 Total Database Records: {count:,}")
        
    conn.close()

except Exception as e:
    st.error(f"Database System Status Error: {str(e)}")

st.markdown("---")


# --- Temporary CSV Debug Section: drug_data.csv Inspection ---
try:
    st.subheader("🔍 drug_data.csv Inspection")

    df_drugs = pd.read_csv("drug_data.csv")

    st.write("Columns:")
    st.write(df_drugs.columns.tolist())

    st.write("Shape:")
    st.write(df_drugs.shape)

    st.dataframe(df_drugs.head(10))
except Exception as csv_err:
    st.error(f"drug_data.csv Load Error: {str(csv_err)}")
