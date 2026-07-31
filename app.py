import streamlit as st
from database.db import get_connection

st.set_page_config(page_title="RxShield")

st.title("🛡️ RxShield")

try:

    conn = get_connection()

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    st.success("Database Connected ✅")

    st.write(tables)

    conn.close()

except Exception as e:

    st.error(str(e))
