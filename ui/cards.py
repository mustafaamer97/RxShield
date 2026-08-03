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

        st.markdown("### ⚠️ Clinical Advice")

        for item in items:
            st.markdown(f"- {item}")

        if recommendation:
            st.divider()
            st.success(f"**Recommendation**\n\n{recommendation}")

        if reference:
            st.caption("📚 Source: DrugBank 6.0 (Knox et al., 2024)")
