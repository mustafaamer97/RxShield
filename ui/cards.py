import streamlit as st

def clinical_card(
    title: str,
    category: str,
    items,
    recommendation: str | None = None,
    reference: str | None = None,
):
    with st.container(border=True):
        st.subheader(f"🛡️ {title}")
        st.markdown(f"**📂 Category:** {category}")
        st.divider()

        # 1. التعديل الأول: تغيير العنوان إلى تفاعلات غذائية أو دوائية حسب نوع التقرير
        if "Food" in title:
            st.markdown("### 🥗 Food Interactions")
        else:
            st.markdown("### 💊 Clinical Interactions")

        # 2. التعديل الثاني: الترقيم الذكي بدلاً من النقاط العشوائية
        for i, item in enumerate(items, start=1):
            st.markdown(f"**{i}.** {item}")

        if recommendation:
            st.divider()
            st.success(f"**Recommendation**\n\n{recommendation}")

        if reference:
            # 3. التعديل الثالث: تقصير المرجع ليصبح مختصر وعملي للمستخدم السريري
            st.caption("📚 Source: DrugBank 6.0")
