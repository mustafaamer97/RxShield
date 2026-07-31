import streamlit as st
from database.db import get_connection
# 1. استيراد قواميس الترجمة والأسماء من ملف الـ loader الخاص بك
from database.loader import NAME_TO_ID, ID_TO_NAME

st.set_page_config(page_title="RxShield")

st.title("🛡️ RxShield")

# --- الجزء الأول: اختبار البحث عن الأدوية (Drug Search Test) ---
st.subheader("Drug Search Test")

drug_name = st.text_input("Drug Name", placeholder="مثال: Lepirudin")

if drug_name:
    # تحويل النص للحروف الصغيرة لضمان مطابقة الأسماء في القاموس بشكل صحيح
    drug_id = NAME_TO_ID.get(drug_name.strip().lower())

    if drug_id:
        st.success(f"DrugBank ID: {drug_id}")
        st.write(f"Drug Name: {ID_TO_NAME[drug_id]}")
    else:
        st.error("Drug not found")

st.markdown("---") # خط فاصل لتنظيم محتوى الصفحة

# --- الجزء الثاني: الاتصال بقاعدة البيانات وعرض العينة ---
try:
    conn = get_connection()
    st.success("Database Connected ✅")

    # جلب اسم أول جدول متوفر
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchone()

    if table:
        try:
            table_name = table["name"]
        except (TypeError, IndexError):
            table_name = table[0]

        st.write("Table Identified:", table_name)

        # حساب العدد الإجمالي للسجلات
        count = conn.execute(
            f"SELECT COUNT(*) FROM `{table_name}`;"
        ).fetchone()[0]

        st.write("Total Records:", f"{count:,}")
        
        # جلب وعرض أول 5 تفاعلات دوائية
        rows = conn.execute(
            f"SELECT * FROM `{table_name}` LIMIT 5;"
        ).fetchall()

        st.subheader("First 5 Drug Interactions")

        for row in rows:
            try:
                st.write(dict(row))
            except (TypeError, ValueError):
                st.write(list(row))
                
    else:
        st.warning("⚠️ Connected, but no tables found in the database.")

    conn.close()

except Exception as e:
    st.error(f"Database Error: {str(e)}")
