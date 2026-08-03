import streamlit as st


def clinical_card(
    title: str,
    message: str,
    category: str = "Information",
    recommendation: str | None = None,
    reference: str | None = None,
):
    """
    Universal RxShield Clinical Card
    Used for DDI and DFI.
    """

    st.markdown(
        f"""
<div style="
border-left:6px solid #ff4b4b;
padding:18px;
margin-bottom:15px;
border-radius:10px;
background:#1b1b1b;
">

<h4 style="margin-bottom:8px;">
🛡️ {title}
</h4>

<b>Category</b><br>
{category}

<br><br>

<b>Clinical Advice</b><br>
{message}

""",
        unsafe_allow_html=True,
    )

    if recommendation:
        st.markdown(
            f"""
<b>Recommendation</b><br>
{recommendation}
""",
            unsafe_allow_html=True,
        )

    if reference:
        st.markdown(
            f"""
<br>

<small><b>Reference:</b><br>
{reference}</small>
""",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
