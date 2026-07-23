import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(
    page_title="RxShield - Clinical Decision Support",
    page_icon="💊",
    layout="wide"
)

# تنسيق CSS مخصص لتحسين مظهر الواجهة
st.markdown("""
    <style>
    .main-header { font-size: 24px; color: #2e6c80; font-weight: bold; }
    .card { background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2e6c80; color: #333; }
    </style>
""", unsafe_allow_html=True)

st.title("💊 RxShield: Clinical Interaction System")
st.markdown("نظام ذكي متطوّر لفحص التفاعلات السريرية وتقديم التوصيات الغذائية والدوائية.")

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
    st.sidebar.success(f"قاعدة البيانات متصلة ({len(df_data)} سجل)")
else:
    st.sidebar.error("ملف البيانات غير موجود في المستودع.")

st.subheader("🔍 البحث السريري المتقدم")
drug_query = st.text_input("أدخل اسم الدواء (مثال: Warfarin):", "")

if st.button("بحث وتدقيق"):
    if not drug_query:
        st.warning("الرجاء كتابة اسم الدواء.")
    elif df_data is None:
        st.error("لا يمكن إجراء الفحص لعدم توفر قاعدة البيانات.")
    else:
        with st.spinner("جاري جلب التحليلات السريرية..."):
            results = df_data[df_data.apply(lambda row: row.astype(str).str.contains(drug_query, case=False).any(), axis=1)]
            
            if not results.empty:
                st.success(f"تم العثور على {len(results)} سجل تطابق الدواء: {drug_query}")
                
                for idx, row in results.iterrows():
                    drug_name = row.get('name', 'غير متوفر')
                    interactions = row.get('food_interactions', 'لا توجد تفاصيل غذائية مسجلة')
                    ref = row.get('reference', 'غير متوفرة')
                    
                    st.markdown(f"""
                        <div class="card">
                            <h4>💊 الدواء: {drug_name}</h4>
                            <p><b>🥗 التفاعلات الغذائية والتوجيهات:</b> {interactions}</p>
                            <p style="font-size: 12px; color: gray;"><b>📚 المرجع العلمي:</b> {ref}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"لا توجد تفاعلات مسجلة للدواء: {drug_query}")

st.markdown("---")
st.markdown("RxShield Clinical System © 2026 | دعم القرار السريري الآمن")
