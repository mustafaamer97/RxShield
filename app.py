import streamlit as st
from database.db import get_connection

st.set_page_config(page_title="RxShield")

st.title("🛡️ RxShield")

try:
    # 1. إنشاء الاتصال بقاعدة البيانات
    conn = get_connection()
    st.success("Database Connected ✅")

    # 2. جلب اسم أول جدول متوفر في قاعدة البيانات
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchone()

    if table:
        # إذا كانت قاعدة البيانات تستخدم sqlite3.Row، يمكننا الوصول عبر المفتاح ["name"]
        # وإلا سنصل إليها عبر الفهرس [0] لضمان التوافق:
        try:
            table_name = table["name"]
        except (TypeError, IndexError):
            table_name = table[0]

        st.write("Table:", table_name)

        # 3. حساب العدد الإجمالي للسجلات داخل هذا الجدول
        count = conn.execute(
            f"SELECT COUNT(*) FROM `{table_name}`;"
        ).fetchone()[0]

        st.write("Total Records:", f"{count:,}")
    else:
        st.warning("⚠️ Connected, but no tables found in the database.")

    # 4. إغلاق الاتصال
    conn.close()

except Exception as e:
    st.error(str(e))
