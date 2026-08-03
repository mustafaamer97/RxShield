import json
import pandas as pd
import streamlit as st
from database.db import get_connection, get_interaction
# استيراد الدالتين معاً من المحرك الإكلينيكي
from utils.clinical_engine import build_report, render_report

class DrugFoodInteractionEngine:
    def __init__(self):
        try:
            with open("Drug to Food interactions Dataset.json", "r", encoding="utf-8") as f:
                self.food_db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.food_db = []

    def find_interactions(self, drug_name: str):
        if not drug_name:
            return None

        # تحويل النص لحروف صغيرة موحدة وإزالة الفراغات الزائدة
        query = drug_name.strip().casefold()

        for item in self.food_db:
            # محاولة جلب اسم الدواء من المفاتيح المتوقعة (drug أو name)
            name = item.get("drug", item.get("name", "")).strip().casefold()
            
            # مطابقة مرنة فائقة (تطابق كامل، أو احتواء نصي متبادل)
            if query == name or query in name or name in query:
                return item

        return None

# تهيئة المحرك
dfi_engine = DrugFoodInteractionEngine()


st.set_page_config(
    page_title="RxShield",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ RxShield")

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


# ====================================================================
# ✨ إنشاء التبويبات لفصل الميزتين بشكل احترافي
# ====================================================================
tab1, tab2 = st.tabs(["💊 Drug–Drug Interaction", "🍎 Drug–Food Interaction"])

# --------------------------------------------------------------------
# التبويب الأول: تفاعلات الأدوية مع بعضها البعض
# --------------------------------------------------------------------
with tab1:
    st.subheader("Drug–Drug Interaction Checker")

    col1, col2 = st.columns(2)

    with col1:
        drug1 = st.selectbox(
            "Drug 1",
            drug_names,
            index=None,
            placeholder="Type drug name...",
            key="dd_drug1"
        )

    with col2:
        drug2 = st.selectbox(
            "Drug 2",
            drug_names,
            index=None,
            placeholder="Type drug name...",
            key="dd_drug2"
        )

    if st.button("Check Interaction", use_container_width=True, key="btn_dd_check"):

        if not drug1 or not drug2:
            st.warning("Please select both drugs.")
            st.stop()

        drug1_id = NAME_TO_ID[drug1]
        drug2_id = NAME_TO_ID[drug2]

        row = get_interaction(drug1_id, drug2_id)

        if row is None:
            st.success("✅ No interaction found.")
        else:
            interaction_text = row["interaction_type"] if "interaction_type" in row.keys() else row["Interaction"]
            report = build_report(interaction_text, drug1, drug2)
            render_report(report)


# --------------------------------------------------------------------
# التبويب الثاني: تفاعلات الأدوية مع الأطعمة (الميزة الجديدة المضافة والمعدلة)
# --------------------------------------------------------------------
with tab2:
    st.subheader("Drug–Food Interaction Checker")
    
    # 🔍 لوحة فحص ذكية تظهر مباشرة على الهاتف لمعرفة سبب عدم المطابقة
    st.info("📊 Debugging Food DB JSON (منفذ الفحص السريع للهاتف):")
    if dfi_engine.food_db:
        st.write("• إجمالي السجلات داخل ملف الأطعمة:", len(dfi_engine.food_db))
        st.write("• شكل أول عنصر بالكامل لمعرفة أسماء المفاتيح (Keys):", dfi_engine.food_db[0])
        
        # استخراج عينة لأول 5 أسماء أدوية مسجلة في الـ JSON لنرى طريقة كتابتها
        sample_names = [item.get("drug", item.get("name", "لم يتم العثور على مفتاح الاسم")) for item in dfi_engine.food_db[:5]]
        st.write("• عينة لأول 5 أسماء أدوية في ملف الـ JSON:", sample_names)
    else:
        st.error("❌ ملف JSON فارغ أو لم يتم تحميله من المسار الصحيح!")
    
    st.markdown("---")

    # اختيار دواء واحد لفحص تفاعلاته الغذائية
    selected_food_drug = st.selectbox(
        "Select Drug",
        drug_names,
        index=None,
        placeholder="Type drug name...",
        key="df_drug"
    )
    
    if st.button("Check Food Interaction", use_container_width=True, key="btn_df_check"):
        if not selected_food_drug:
            st.warning("Please select a drug.")
            st.stop()
            
        result = dfi_engine.find_interactions(selected_food_drug)

        if result:
            st.subheader("🥦 Drug–Food Interactions")

            # جلب تفاعلات الأطعمة من المفتاح المخصص لها داخل القاموس
            # تم استخدام .get() لحماية الكود من الانهيار إذا اختلف اسم المفتاح في بعض الصفوف
            interactions = result.get("food_interactions", result.get("interactions", []))
            
            if isinstance(interactions, list) and interactions:
                for interaction in interactions:
                    st.warning(interaction)
            elif isinstance(interactions, str):
                st.warning(interactions)
            else:
                st.info("No specific food interactions text listed in this object.")

            # عرض المصدر المرجعي الطبي إن وجد
            reference = result.get("reference", result.get("source"))
            if reference:
                st.caption(f"**Reference:** {reference}")
        else:
            st.error(f"❌ لم يتم العثور على مطابقة للدواء '{selected_food_drug}' داخل ملف الـ JSON الحالي.")
