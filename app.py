import streamlit as st
import pandas as pd
import gdown
import os
import json

st.set_page_config(
    page_title="RxShield | Clinical Decision",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ تطبيق RxShield لفحص التداخلات الدوائية")

# تعريف كلاس المحرك مباشرة داخل الملف لتجنب أي مشاكل استيراد
class RxShieldEngine:
    def __init__(self):
        self.drug_info = {}
        self.synonyms = {}
        self.food_db = {}
        self.ddi_df = None

    def load_data(self):
        # تحميل ملفات الـ JSON الموجودة عندك في المستودع إذا لزم الأمر
        if os.path.exists('drug_info.json'):
            with open('drug_info.json', 'r', encoding='utf-8') as f:
                self.drug_info = json.load(f)
        
        if os.path.exists('drugs_synonyms.json'):
            with open('drugs_synonyms.json', 'r', encoding='utf-8') as f:
                self.synonyms = json.load(f)

# رابط ملف الـ 150 ميجابايت على جوجل درايف
file_id = "1FEhCYlAOewAfCaBAyyncDDIvQJoo8G3x"
url = f'https://drive.google.com/uc?id={file_id}'
output = 'all_id_interaction.csv'

@st.cache_data
def load_large_database():
    if not os.path.exists(output):
        with st.spinner('جاري تحميل قاعدة البيانات الكبيرة من جوجل درايف، يرجى الانتظار قليلاً...'):
            gdown.download(url, output, quiet=False)
    df = pd.read_csv(output)
    return df

# تشغيل المحرك وتحميل البيانات
engine = RxShieldEngine()
engine.load_data()

df = load_large_database()

st.success("تم تشغيل التطبيق وقاعدة البيانات بنجاح تام!")
st.write(f"إجمالي عدد التداخلات في القاعدة: {df.shape[0]} صف")

# عرض عينة من البيانات للتأكد
st.dataframe(df.head())

