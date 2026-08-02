import streamlit as st
import pandas as pd
from database.db import get_interaction
from utils.clinical_engine import build_report

st.set_page_config(
    page_title="RxShield",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ RxShield")
st.subheader("Drug–Drug Interaction Checker")

# 1. تحميل ملف الأدوية المفلتر الجديد
drug_lookup = pd.read_csv("drug_lookup.csv")

# 2. بناء القواميس ديناميكياً من الملف
NAME_TO_ID = dict(zip(drug_lookup["drug_name"], drug_lookup["drug_id"]))

# 3. بناء قائمة الأسماء المرتبة أبجدياً لواجهة المستخدم
drug_names = sorted(drug_lookup["drug_name"].tolist())

col1, col2 = st.columns(2)

with col1:
    drug1 = st.selectbox(
        "Drug 1",
        drug_names,
        index=None,
        placeholder="Select first drug"
    )

with col2:
    drug2 = st.selectbox(
        "Drug 2",
        drug_names,
        index=None,
        placeholder="Select second drug"
    )

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
        # ملاحظة: تأكد أن مفتاح العلاقة في قاعدة بياناتك يطابق الاسم المستدعى هنا (مثال: 'interaction_type' أو 'Interaction')
        interaction_text = row["interaction_type"] if "interaction_type" in row.keys() else row["Interaction"]
        
        report = build_report(
            interaction_text,
            drug1,
            drug2
        )

        st.error(f"Severity: {report['severity']}")

        st.markdown("### Clinical Interaction")

        st.write(report["interaction"])
