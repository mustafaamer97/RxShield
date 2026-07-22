
import streamlit as st
from rxshield_engine import rxshield_engine

# ===============================
# Page
# ===============================

st.set_page_config(
    page_title="RxShield",
    page_icon="🛡️",
    layout="wide"
)

# ===============================
# Header
# ===============================

st.title("🛡️ RxShield")
st.caption("Clinical Drug Interaction Checker")

st.divider()

# ===============================
# Inputs
# ===============================

col1, col2 = st.columns(2)

with col1:
    drug1 = st.text_input(
        "Drug 1",
        placeholder="Example: Warfarin"
    )

with col2:
    drug2 = st.text_input(
        "Drug 2",
        placeholder="Example: Aspirin"
    )

# ===============================
# Button
# ===============================

if st.button("🔍 Check Interaction", use_container_width=True):

    if not drug1 or not drug2:

        st.warning("Please enter both drugs.")

    else:

        report = rxshield_engine(drug1, drug2)

        # -----------------------------
        # Errors
        # -----------------------------

        if report.get("success") is False:

            st.error(report["error"])

        elif report["interaction_found"] is False:

            st.success("✅ No clinically significant interaction found.")

        else:

            severity = report["severity"]

            if severity == "Contraindicated":
                st.error(f"⛔ {severity}")

            elif severity == "Major":
                st.error(f"🔴 {severity}")

            elif severity == "Moderate":
                st.warning(f"🟠 {severity}")

            else:
                st.info(f"🟢 {severity}")

            st.subheader("Interaction")

            st.write(report["interaction"])

            st.subheader("Mechanism")

            st.write(report["mechanism"])

            st.subheader("Clinical Management")

            st.write(report["clinical_management"])

            st.subheader("Evidence")

            st.write(report["evidence"])

            # -----------------------------
            # Adverse Effects
            # -----------------------------

            if report["adverse_effects"]:

                st.subheader("Adverse Effects")

                for effect in report["adverse_effects"]:
                    st.markdown(f"- {effect}")

            # -----------------------------
            # Food Interactions
            # -----------------------------

            if report["food1"]:

                st.subheader(f"Food Interactions ({report['drug1']['name']})")

                for item in report["food1"]["food_interactions"]:
                    st.markdown(f"- {item}")

            if report["food2"]:

                st.subheader(f"Food Interactions ({report['drug2']['name']})")

                for item in report["food2"]["food_interactions"]:
                    st.markdown(f"- {item}")
