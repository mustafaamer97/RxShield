import streamlit as st


def clinical_card(
    title,
    message,
    category="Clinical Information",
    recommendation=None,
    reference=None,
):

    st.markdown(
        f"""
<div style="
background-color:#F8F9FA;
padding:18px;
margin-top:12px;
margin-bottom:18px;
border-radius:12px;
border-left:6px solid #D32F2F;
box-shadow:0px 2px 8px rgba(0,0,0,0.08);
">

<h4 style="margin-bottom:10px;">
🛡️ {title}
</h4>

<p style="margin-bottom:6px;">
<b>📂 Category</b><br>
{category}
</p>

<p style="margin-bottom:6px;">
<b>⚠️ Clinical Advice</b><br>
{message}
</p>
""",
        unsafe_allow_html=True,
    )

    if recommendation:
        st.markdown(
            f"""
<p style="margin-bottom:6px;">
<b>✅ Recommendation</b><br>
{recommendation}
</p>
""",
            unsafe_allow_html=True,
        )

    if reference:
        st.markdown(
            """
<p style="margin-bottom:0px;">
<b>📚 Source</b><br>
DrugBank 6.0 (Knox et al., 2024)
</p>
""",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
