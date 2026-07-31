import streamlit as st
import json
import zipfile
import pandas as pd
from database.db import get_connection
from database.loader import NAME_TO_ID, ID_TO_NAME
from database.db import get_interaction

st.set_page_config(page_title="RxShield")

# --- Temporary ZIP/CSV Structural Check Section ---
try:
    st.subheader("🔍 Temporary ZIP/CSV Structural Check")
    with zipfile.ZipFile("data_final_v5.zip", "r") as z:
        st.write("Files in ZIP:", z.namelist())
        
        # Extract and read the first CSV file found inside the archive
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
    # Fetch and display the first key-value pair to inspect structural architecture
    st.write(next(iter(debug_data.items())))
    st.markdown("---")
except Exception as json_err:
    st.error(f"Temporary JSON Load Error: {str(json_err)}")
    st.markdown("---")


# --- Main Application: Drug–Drug Interaction Checker ---
st.header("🛡️ Drug–Drug Interaction Checker")

# Prepare alphabetically sorted drug names list
drug_names = sorted(NAME_TO_ID.keys())

# Split user interface into two columns for side-by-side selection
col1, col2 = st.columns(2)

with col1:
    drug1 = st.selectbox("Drug 1", drug_names, index=None, placeholder="Select first drug")

with col2:
    drug2 = st.selectbox("Drug 2", drug_names, index=None, placeholder="Select second drug")

# Interaction verification triggering mechanism
if st.button("Check Interaction", use_container_width=True):
    if drug1 and drug2:
        drug1_id = NAME_TO_ID[drug1]
        drug2_id = NAME_TO_ID[drug2]
        
        # Execute cross-referencing search query using IDs
        result = get_interaction(drug1_id, drug2_id)

        if result:
            st.success("Interaction Found ✅")
            try:
                # Output interaction details as a clean dictionary schema
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
    
    # Extract the schema identifier for the active data table
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchone()

    if table:
        try:
            table_name = table["name"]
        except (TypeError, IndexError):
            table_name = table[0]

        st.caption(f"⚡ Connected to system database table: `{table_name}`")
        
        # Compute and parse total entry metric inside the targeted table
        count = conn.execute(
            f"SELECT COUNT(*) FROM `{table_name}`;"
        ).fetchone()[0]
        st.caption(f"📊 Total Database Records: {count:,}")
        
    conn.close()

except Exception as e:
    st.error(f"Database System Status Error: {str(e)}")
