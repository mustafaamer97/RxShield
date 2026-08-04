import json
import pandas as pd
import streamlit as st
from database.db import get_connection, get_interaction
# 📥 استيراد محرك معلومات الأدوية الجديد
from engine.drug_info_engine import DrugInfoEngine
# 📥 استيراد الكارت السريري 
from ui.cards import clinical_card
# استيراد الدالتين معاً من المحرك الإكلينيكي
from utils.clinical_engine import build_report, render_report

# تهيئة محرك معلومات الأدوية
drug_info_engine = DrugInfoEngine()


class DrugFoodInteractionEngine:

    def __init__(self):
        try:
            with open(
                "Drug to Food interactions Dataset.json",
                "r",
                encoding="utf-8",
            ) as f:
                self.food_db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.food_db = []

    def find_interactions(self, drug_name: str):
        if not drug_name:
            return None

        # تنظيف وتحويل نص البحث لحروف صغيرة
        query = drug_name.strip().casefold()
        # استخراج الكلمة الأولى من اسم الدواء للبحث المرن (مثال: Warfarin Sodium تصبح warfarin)
        query_first_word = query.split()[0] if query.split() else query

        for item in self.food_db:
            name = item.get("name", "").strip().casefold()

            # مطابقة ذكية فائقة المرونة
            if (
                query == name
                or query in name
                or name in query
                or query_first_word in name
            ):
                return item

        return None


# تهيئة محرك التفاعلات الغذائية
dfi_engine = DrugFoodInteractionEngine()

st.set_page_config(page_title="RxShield", page_icon="🛡️", layout="wide")

st.title("🛡️ RxShield")

# تحميل ملف الأدوية المفلتر الجديد
drug_lookup = pd.read_csv("drug_lookup.csv")

# جلب المعرفات الفريدة من قاعدة البيانات
conn = get_connection()

drug1_ids = pd.read_sql_query(
    "SELECT DISTINCT [Drug1 ID] AS drug_id FROM interactions", conn
)
drug2_ids = pd.read_sql_query(
    "SELECT DISTINCT [Drug2 ID] AS drug_id FROM interactions", conn
)

valid_ids = pd.concat([drug1_ids, drug2_ids]).drop_duplicates()

# تصفية أدوية الواجهة لبناء القواميس
filtered_lookup = drug_lookup.merge(valid_ids, on="drug_id", how="inner")
NAME_TO_ID = dict(zip(filtered_lookup["drug_name"], filtered_lookup["drug_id"]))
drug_names = sorted(filtered_lookup["drug_name"].tolist())

st.success(f"Loaded {len(drug_names)} valid RxShield drugs")

# ====================================================================
# ✨ التبويبات الرسمية والتطبيق المستقر
# ====================================================================
tab1, tab2 = st.tabs(
    ["💊 Drug–Drug Interaction", "🍎 Drug–Food Interaction"]
)

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
            key="dd_drug1",
        )

    with col2:
        drug2 = st.selectbox(
            "Drug 2",
            drug_names,
            index=None,
            placeholder="Type drug name...",
            key="dd_drug2",
        )

    if st.button(
        "Check Interaction", use_container_width=True, key="btn_dd_check"
    ):
        if not drug1 or not drug2:
            st.warning("Please select both drugs.")
            st.stop()

        drug1_id = NAME_TO_ID[drug1]
        drug2_id = NAME_TO_ID[drug2]

        row = get_interaction(drug1_id, drug2_id)

        if row is None:
            st.success("✅ No interaction found.")
        else:
            interaction_text = (
                row["interaction_type"]
                if "interaction_type" in row.keys()
                else row["Interaction"]
            )
            
            # بناء التقرير
            report = build_report(interaction_text, drug1, drug2)
            
            # تمرير النص داخل قائمة [ ] ليتوافق مع حقل items في الدالة المتوفرة لديك
            clinical_card(
                title="Drug–Drug Interaction Report",
                category=report["severity"],
                items=[report["interaction"]],
                recommendation=report["recommendation"],
                reference="DrugBank Knowledge Base",
            )
            
            # إضافة قائمة التفاصيل الممتدة السريرية بعد البطاقة مباشرة
            with st.expander("🩺 Clinical Details"):
                st.markdown("**Mechanism**")
                st.write(report["mechanism"])
                
                st.markdown("**Monitoring**")
                st.write(report["monitoring"])


# --------------------------------------------------------------------
# التبويب الثاني: تفاعلات الأدوية مع الأطعمة
# --------------------------------------------------------------------
with tab2:
    st.subheader("Drug–Food Interaction Checker")

    # اختيار دواء واحد لفحص تفاعلاته الغذائية
    selected_food_drug = st.selectbox(
        "Select Drug",
        drug_names,
        index=None,
        placeholder="Type drug name...",
        key="df_drug",
    )

    if st.button(
        "Check Food Interaction", use_container_width=True, key="btn_df_check"
    ):
        if not selected_food_drug:
            st.warning("Please select a drug.")
            st.stop()

        result = dfi_engine.find_interactions(selected_food_drug)

        if result:
            # جلب مصفوفة التفاعلات بأمان
            raw_interactions = result.get("food_interactions", [])
            
            # التأكد من تحويل النص إلى قائمة إذا كان نصاً مفرداً لتجنب الأخطاء البرمجية
            food_items = raw_interactions if isinstance(raw_interactions, list) else [raw_interactions]

            # الاستدعاء المباشر النظيف
            clinical_card(
                title="Drug–Food Interaction Report",
                category="Food Safety",
                items=food_items,
                recommendation="Maintain a consistent diet and consult your healthcare provider before making major dietary changes.",
                reference=result.get("reference"),
            )
        else:
            st.success("✅ No specific food interactions found.")
