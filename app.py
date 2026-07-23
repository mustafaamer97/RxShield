import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="RxShield - Clinical Drug Interaction Checker",
    page_icon="💊",
    layout="wide"
)

st.title("💊 RxShield: Clinical Drug & Food Interaction System")
st.markdown("نظام ذكي متكامل لفحص التفاعلات الدوائية والتغذوية وتقديم التوصيات السريرية الفورية.")

# مسار ملف الـ JSON المرفوع حديثاً في غيت هب
json_file_path = "Drug to Food interactions Dataset.json"

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return None

df_data = load_data(json_file_path)

if df_data is not None:
    st.success(f"قاعدة البيانات جاهزة بنجاح (عدد السجلات: {len(df_data)})")
else:
    st.error("تنبيه: تأكد من أن اسم ملف الـ JSON مطابق تماماً في غيت هب.")

st.subheader("🔍 استعلام التفاعلات السريرية")
drug_query = st.text_input("أدخل اسم الدواء للبحث (مثال: Warfarin أو Aspirin):", "")

if st.button("بدء الفحص السريري"):
    if not drug_query:
        st.warning("الرجاء كتابة اسم دواء في خانة البحث.")
    elif df_data is None:
        st.error("لا يمكن إجراء الفحص لعدم تحميل ملف البيانات.")
    else:
        with st.spinner("جاري تحليل البيانات ومطابقة التفاعلات..."):
            results = df_data[df_data.apply(lambda row: row.astype(str).str.contains(drug_query, case=False).any(), axis=1)]
            
            if not results.empty:
                st.success(f"تم العثور على {len(results)} نتيجة مطابقة للدواء: {drug_query}")
                st.dataframe(results, use_container_width=True)
            else:
                st.warning(f"لم يتم العثور على تفاعلات مسجلة للدواء: {drug_query}")

st.markdown("---")
st.markdown("RxShield Clinical Decision Support System © 2026 | تم التطوير لدعم الرعاية السريرية الآمنة.")
