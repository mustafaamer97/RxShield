import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from database.db import get_connection
from database.drug_service import (
    DRUG_NAMES,
    NAME_TO_ID,
    ID_TO_NAME,
)
from database.db import get_interaction

st.set_page_config(page_title="RxShield")


# --- Main Application: Drug–Drug Interaction Checker ---
st.header("🛡️ Drug–Drug Interaction Checker")

drug_names = DRUG_NAMES

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
