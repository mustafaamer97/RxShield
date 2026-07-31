import streamlit as st
import sqlite3
from pathlib import Path

st.set_page_config(page_title="RxShield", layout="wide")

st.title("🛡️ RxShield CDSS")

DB_PATH = Path("all_id_interaction.db")

if not DB_PATH.exists():
    st.error("❌ Database not found.")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    st.success("✅ Database connected successfully")

    st.write("Tables:")

    st.write(tables)

    conn.close()

except Exception as e:
    st.error(e)
