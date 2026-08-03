import streamlit as st
import pandas as pd
from database.db import get_interaction, get_connection
# استيراد الدالتين معاً من المحرك الإكلينيكي
from utils.clinical_engine import build_report, render_report

st.set_page_config(
    page_title="RxShield",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ RxShield")
st.subheader("Drug–Drug Interaction Checker")

# 1. تحميل ملف الأدوية المفلتر الجديد
drug_lookup = pd.read_csv("drug_lookup.csv")

# ----------------- الفحص الأول (بعد قراءة الملف مباشرة) -----------------
st.write("Atorvastatin exists:", "Atorvastatin" in drug_lookup["drug_name"].tolist())
st.write(
    drug_lookup[
        drug_lookup["drug_name"].str.contains(
            "Ator", case=False, na=False
        )
    ]
)
st.markdown("---")
# -----------------------------------------------------------------------

# ----------------- أسطر الفحص القديمة -----------------
st.write("### 🔍 Debugging Info (بيانات فحص الملف):")
st.write(drug_lookup.head())
st.write("Rows:", len(drug_lookup))
st.write("First 30 names:")
st.write(drug_lookup["drug_name"].head(30))
st.write("Columns in CSV:", drug_lookup.columns)
st.markdown("---")

# معاينة أول 10 صفوف من البيانات على الواجهة فوراً
st.write(drug_lookup.head(10))

# ----------------- الكود المعدل لجلب المعرفات الفريدة بشكل صحيح -----------------
conn = get_connection()

drug1_ids = pd.read_sql_query(
    """
    SELECT DISTINCT [Drug1 ID] AS drug_id
    FROM interactions
    """,
    conn,
)

drug2_ids = pd.read_sql_query(
    """
    SELECT DISTINCT [Drug2 ID] AS drug_id
    FROM interactions
    """,
    conn,
)

valid_ids = (
    pd.concat([drug1_ids, drug2_ids])
    .drop_duplicates()
)

st.write("### 📊 Interactions Database Check:")
st.write("Unique Drug IDs:", len(valid_ids))
st.write(valid_ids.head())
# ----------------------------------------------------------------------------------

# تصفية drug_lookup بحيث تبقى فقط الأدوية الموجودة في قاعدة التفاعلات
filtered_lookup = drug_lookup.merge(valid_ids, on="drug_id", how="inner")

# بناء القواميس من البيانات المفلترة
NAME_TO_ID = dict(zip(filtered_lookup["drug_name"], filtered_lookup["drug_id"]))

# قائمة الأدوية النهائية للواجهة
drug_names = sorted(filtered_lookup["drug_name"].tolist())

# ----------------- الفحص الثاني (بعد بناء قائمة drug_names النهائية) -----------------
st.write("Total names:", len(drug_names))
st.write(
    [x for x in drug_names if "ator" in x.lower()]
)
st.markdown("---")
# ----------------------------------------------------------------------------------

st.success(f"Loaded {len(drug_names)} valid RxShield drugs")

col1, col2 = st.columns(2)

# ----------------- صناديق الاختيار -----------------
with col1:
    drug1 = st.selectbox(
        "Drug 1",
        drug_names,
        index=None,
        placeholder="Type drug name..."
    )

with col2:
    drug2 = st.selectbox(
        "Drug 2",
        drug_names,
        index=None,
        placeholder="Type drug name..."
    )
# ------------------------------------------------------------

if st.button("Check Interaction", use_container_width=True):

    if not drug1 or not drug2:
        st.warning("Please select both drugs.")
        st.stop()

    drug1_id = NAME_TO_ID[drug1]
    drug2_id = NAME_TO_ID[drug2]

    row = get_interaction(drug1_id, drug2_id)

    if row is None:
        st.success("✅ No interaction found.")
    else:
        # التأكد من مطابقة مفتاح التفاعل في قاعدة البيانات
        interaction_text = row["interaction_type"] if "interaction_type" in row.keys() else row["Interaction"]
        
        # بناء التقرير
        report = build_report(
            interaction_text,
            drug1,
            drug2
        )

        # ----------------- عرض التقرير المطور -----------------
        # تم استبدال جميع أسطر العرض القديمة والحذف بالكامل بهذا الاستدعاء النظيف:
        render_report(report)
        # -------------------------------------------------------------------
