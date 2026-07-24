import streamlit as st
from engine import RxShieldEngine

st.set_page_config(
    page_title="RxShield | Clinical Decision Support",
    page_icon="🛡️",
    layout="wide"
)

# تصميم عصري واحترافي للواجهة الطبية
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; height: 48px; background-color: #0284c7; color: white; border: none; transition: 0.2s; }
    .stButton>button:hover { background-color: #0369a1; }
    
    /* تنسيق الكروت الطبية الحديثة */
    .medical-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    .patient-box {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
    }
    .clinical-box {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
    }
    .warning-banner {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        padding: 16px;
        border-radius: 8px;
        color: #991b1b;
        font-weight: 600;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_engine():
    eng = RxShieldEngine()
    eng.load()
    return eng

with st.sidebar:
    st.image("https://img.icons8.com/color/96/pill.png", width=60)
    st.markdown("### **RxShield CDSS**")
    st.markdown("Professional Clinical Intelligence & Safety Engine.")
    st.markdown("---")
    st.markdown("🟢 **System Status:** Online")
    st.markdown("🔒 **Security:** HIPAA Aligned")

with st.spinner("Initializing clinical data layers..."):
    engine = load_engine()

# العنوان الرئيسي الراقي
st.markdown("## 🛡️ RxShield Clinical Intelligence Platform")
st.markdown("Advanced Drug-Drug and Drug-Food Interaction Analysis with Dual-Perspective Insights.")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "💊 Pairwise DDI Explorer", 
    "🧬 Polypharmacy Screening", 
    "🍏 Drug-Food Guidance", 
    "📖 Drug Profile"
])

with tab1:
    st.markdown("### Pairwise Drug Interaction Analysis")
    st.markdown("Evaluate potential pharmacological conflicts between two specific medications.")
    
    col1, col2 = st.columns(2)
    with col1:
        drug1 = st.selectbox("Primary Medication", options=[""] + engine.all_drug_names, key="d1")
    with col2:
        drug2 = st.selectbox("Secondary Medication", options=[""] + engine.all_drug_names, key="d2")
        
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Execute Clinical Analysis", type="primary"):
        if not drug1 or not drug2:
            st.warning("⚠️ Please select both medications to run the analysis.")
        else:
            res = engine.check_ddi(drug1, drug2)
            if res["status"] == "error":
                st.error(f"❌ {res['message']}")
            elif res["status"] == "safe":
                st.success(f"✅ {res['message']}")
            else:
                st.markdown(f"""
                    <div class="medical-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h4 style="margin: 0; color: #1e293b;">Interaction: {res['drug1']} ↔️ {res['drug2']}</h4>
                            <span style="font-size: 16px; font-weight: bold;">{res['severity_icon']} {res['severity_level']}</span>
                        </div>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 10px 0;">
                        
                        <div style="margin-top: 15px;">
                            <strong>👤 Patient Guide:</strong>
                            <div class="patient-box">{res['patient_advice']}</div>
                        </div>
                        
                        <div style="margin-top: 15px;">
                            <strong>🩺 Clinical Management & Pharmacology:</strong>
                            <div class="clinical-box">{res['clinical_management']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("### Polypharmacy Multi-Drug Risk Screening")
    st.markdown("Scan a comprehensive medication list for multi-point pharmacological conflicts.")
    
    selected_drugs = st.multiselect("Select Patient Medication Profile", options=engine.all_drug_names, key="multi_drugs")
    
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Run Polypharmacy Scan", type="primary"):
        if len(selected_drugs) < 2:
            st.warning("⚠️ Please select at least two medications for multi-drug screening.")
        else:
            multi_results = engine.check_multi_ddi(selected_drugs)
            st.markdown(f"#### Screening Results ({len(multi_results)} pairs analyzed)")
            for d1, d2, res in multi_results:
                badge = res.get('severity_icon', '✅') if res['status'] == 'warning' else '✅'
                with st.expander(f"{badge} [{d1}] ↔️ [{d2}] — Status: {res['status'].upper()}"):
                    if res["status"] == "error":
                        st.error(res["message"])
                    elif res["status"] == "safe":
                        st.success(res["message"])
                    else:
                        st.markdown(f"**Risk Level:** {res['severity_icon']} **{res['severity_level']}**")
                        st.markdown(f"**👤 Patient Guide:**\n> {res['patient_advice']}")
                        st.markdown(f"**🩺 Clinical Management:**\n> {res['clinical_management']}")

with tab3:
    st.markdown("### Drug-Food Interaction & Dietary Guidance")
    st.markdown("Review specific nutritional restrictions and pharmacokinetic food impacts.")
    
    drug_food = st.selectbox("Select Medication", options=[""] + engine.all_drug_names, key="df")
    
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Generate Dietary Report", type="secondary"):
        if not drug_food:
            st.warning("⚠️ Please select a medication.")
        else:
            res = engine.check_dfi(drug_food)
            if res["status"] == "error":
                st.error(res["message"])
            elif res["status"] == "safe":
                st.success(res["message"])
            else:
                st.markdown(f"""
                    <div class="medical-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h4 style="margin: 0; color: #1e293b;">Dietary Profile: {res['drug']}</h4>
                            <span style="font-size: 16px; font-weight: bold;">{res['severity_icon']} {res['severity_level']}</span>
                        </div>
                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 10px 0;">
                        
                        <div style="margin-top: 15px;">
                            <strong>👤 Patient Guide:</strong>
                            <div class="patient-box">{res['patient_advice']}</div>
                        </div>
                        
                        <div style="margin-top: 15px;">
                            <strong>⚠️ Structured Dietary Restrictions:</strong>
                            <ul style="margin-top: 5px; color: #334155;">
                """, unsafe_allow_html=True)
                for item in res.get("food_interactions", []):
                    st.markdown(f"<li>{item}</li>", unsafe_allow_html=True)
                st.markdown(f"""
                            </ul>
                        </div>
                        
                        <div style="margin-top: 15px;">
                            <strong>🩺 Clinical Management:</strong>
                            <div class="clinical-box">{res['clinical_management']}</div>
                        </div>
                        
                        <div style="margin-top: 15px; font-size: 13px; color: #64748b;">
                            📚 <strong>Evidence Reference:</strong> {res.get('reference', 'N/A')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

with tab4:
    st.markdown("### Comprehensive Drug Profile Explorer")
    drug_prof = st.selectbox("Search Medication Database", options=[""] + engine.all_drug_names, key="dprof")
    
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("Fetch Drug Profile"):
        if not drug_prof:
            st.warning("⚠️ Please select a medication.")
        else:
            profile = engine.get_drug_profile(drug_prof)
            if profile:
                st.success(f"📖 Database Profile Retrieved for: {drug_prof}")
                st.json(profile)
            else:
                st.warning(f"ℹ️ No extended profile available in the repository.")
