import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="RxShield - Clinical Drug Interaction Checker", page_icon="💊", layout="wide")

st.title("💊 RxShield: Clinical Drug & Food Interaction System")
st.markdown("نظام ذكي متكامل لفحص التفاعلات الدوائية والتغذوية وتقديم التوصيات السريرية الفورية.")

json_file_path = "/kaggle/input/datasets/mustafaamer97/ddi-and-dfi/archive/Drug to Food interactions Dataset.json"

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return None

df_data = load_data(json_file_path)

if df_data is not None:
    st.sidebar.success(f"تم تحميل قاعدة البيانات بنجاح (عدد السجلات: {len(df_data)})")
else:
    st.sidebar.error("تنبيه: لم يتم العثور على ملف البيانات في المسار المحدد.")

st.subheader("🔍 استعلام التفاعلات السريرية")
drug_query = st.text_input("أدخل اسم الدواء للبحث عن تفاعلاته (مثال: Warfarin, Aspirin):", "")

if st.button("بدء الفحص السريري"):
    if drug_query and df_data is not None:
        with st.spinner("جاري تحليل البيانات ومطابقة التفاعلات..."):
            results = df_data[df_data.apply(lambda row: row.astype(str).str.contains(drug_query, case=False).any(), axis=1)]
            
            if not results.empty:
                st.success(f"تم العثور على {len(results)} نتيجة مطابقة للدواء: {drug_query}")
                st.dataframe(results, use_container_width=True)
            else:
                st.warning(f"لم يتم العثور على تفاعلات مسجلة للدواء: {drug_query}")
    else:
        st.warning("الرجاء إدخال اسم دواء صالح للبحث.")

st.markdown("---")
st.markdown("RxShield Clinical Decision Support System © 2026 | تم التطوير لدعم الرعاية السريرية الآمنة.")
