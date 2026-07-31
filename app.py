import streamlit as st
from database.db import get_connection
# 1. استيراد القواميس ودالة الفحص المطلوبة
from database.loader import NAME_TO_ID, ID_TO_NAME
from database.db import get_interaction

st.set_page_config(page_title="RxShield")

# --- الجزء المحدث: فاحص التداخلات الدوائية (Drug–Drug Interaction Checker) ---
st.header("🛡️ Drug–Drug Interaction Checker")

# تجهيز قائمة الأدوية مرتبة أبجدياً
drug_names = sorted(NAME_TO_ID.keys())

# تقسيم الواجهة إلى عمودين لاختيار الدوائين بجانب بعضهما
col1, col2 = st.columns(2)

with col1:
    drug1 = st.selectbox("Drug 1", drug_names, index=None, placeholder="Select first drug")

with col2:
    drug2 = st.selectbox("Drug 2", drug_names, index=None, placeholder="Select second drug")

# تفعيل زر الفحص
if st.button("Check Interaction", use_container_width=True):
    if drug1 and drug2:
        drug1_id = NAME_TO_ID[drug1]
        drug2_id = NAME_TO_ID[drug2]
        
        # استدعاء دالة الفحص باستخدام المعرفات (IDs)
        result = get_interaction(drug1_id, drug2_id)

        if result:
            st.success("Interaction Found ✅")
            try:
                # عرض تفاصيل التداخل كقاموس منظم
                st.write(dict(result))
            except (TypeError, ValueError):
                st.write(list(result))
        else:
            st.info("No interaction found.")
    else:
        st.warning("⚠️ Please select both drugs to perform the check.")

st.markdown("---") # خط فاصل لتنظيم محتوى الصفحة

# --- الجزء الثاني: التحقق من حالة قاعدة البيانات والجدول بالأسفل ---
try:
    conn = get_connection()
    
    # جلب اسم أول جدول متوفر
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchone()

    if table:
        try:
            table_name = table["name"]
        except (TypeError, IndexError):
            table_name = table[0]

        st.caption(f"⚡ Connected to system database table: `{table_name}`")
        
        # حساب العدد الإجمالي للسجلات وعرضه كمعلومة إحصائية في الأسفل
        count = conn.execute(
            f"SELECT COUNT(*) FROM `{table_name}`;"
        ).fetchone()[0]
        st.caption(f"📊 Total Database Records: {count:,}")
        
    conn.close()
except Exception as e:
    st.error(f"Database System Status Error: {str(import json
with open("drugs_synonyms.json", "r", encoding="utf-8") as f:
    data = json.load(f)

st.write(next(iter(data.items())))
