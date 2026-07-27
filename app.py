import streamlit as st
import pandas as pd
import sqlite3
import requests
import zipfile
import os
import json
import re

st.set_page_config(
    page_title="RxShield | Clinical Decision Support",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ RxShield | Smart Clinical Decision Support")
st.write("Advanced professional engine for checking Drug-Drug and Drug-Food interactions.")

# ========================================================
# 1. Configuration & Database Initialization
# ========================================================
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mustafaamer97/RxShield/main"
ZIP_FILE_URL = f"{GITHUB_RAW_URL}/all_id_interaction.zip"
DB_ZIP_PATH = "all_id_interaction.zip"
DB_FILE_PATH = "all_id_interaction.db"

@st.cache_resource
def init_database():
    if not os.path.exists(DB_FILE_PATH):
        with st.spinner('⏳ First time setup: Initializing secure medical database...'):
            response = requests.get(ZIP_FILE_URL, stream=True)
            if response.status_code == 200:
                with open(DB_ZIP_PATH, 'wb') as f:
                    f.write(response.content)
                with zipfile.ZipFile(DB_ZIP_PATH, 'r') as zip_ref:
                    zip_ref.extractall(".")
                if os.path.exists(DB_ZIP_PATH):
                    os.remove(DB_ZIP_PATH)
            else:
                st.error("❌ Failed to download database.")
                return None
    return sqlite3.connect(DB_FILE_PATH, check_same_thread=False)

db_conn = init_database()

# ========================================================
# 2. Loading Companion Files & Building Search Maps
# ========================================================
@st.cache_data
def load_helper_data():
    synonyms = {}
    food_data = ""
    
    if os.path.exists('drugs_synonyms.json'):
        with open('drugs_synonyms.json', 'r', encoding='utf-8') as f:
            synonyms = json.load(f)
            
    food_file_name = 'Drug to Food interactions ...'
    if os.path.exists(food_file_name):
        with open(food_file_name, 'r', encoding='utf-8') as f:
            food_data = f.read()
            
    # بناء قائمة نظيفة بالأسماء مرتبة أبجدياً للـ Selectbox
    dropdown_list = []
    id_to_name = {}
    for drug_id, syn_list in synonyms.items():
        if syn_list:
            # نأخذ أول اسم كإسم أساسي ونعرض الـ ID بجانبه للمصداقية الطبية
            primary_name = str(syn_list[0]).strip().capitalize()
            display_string = f"{primary_name} ({drug_id.upper()})"
            dropdown_list.append(display_string)
            id_to_name[drug_id.upper()] = primary_name
            # ربط كل المترادفات الأخرى بنفس المعرف لضمان دقة البحث بالخلفية
            for syn in syn_list:
                id_to_name[str(syn).strip().lower()] = drug_id.upper()
                
    return synonyms, food_data, sorted(dropdown_list), id_to_name

synonyms_dict, food_interactions_text, sorted_drugs_list, name_to_id_map = load_helper_data()

# دالة لتنظيف الرموز الطبية المزعجة وجعل النص احترافي
def clean_interaction_text(text, drug1_name, drug2_name):
    if not text:
        return ""
    # إزالة الرموز مثل (.*) أو تعبيرات النوت بوك القديمة
    cleaned = re.sub(r'\(\.\*\)', '', text)
    cleaned = cleaned.replace("the risk or severity of", "The risk of")
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

# دالة ذكية لتحديد مستوى الخطورة وتلوينها طبيعياً
def get_severity_color(text):
    text_lower = text.lower()
    # كلمات مفتاحية تدل على خطورة عالية جداً
    if any(w in text_lower for w in ["bleeding", "arrhythmia", "qtc prolongation", "toxicity", "fatal", "severe"]):
        return "🔴 High Risk"
    # كلمات تدل على خطورة متوسطة أو تعديل جرعات
    elif any(w in text_lower for w in ["decrease the therapeutic efficacy", "increase the excretion rate"]):
        return "🟡 Moderate Caution"
    else:
        return "🔵 Monitor / Information"

# ========================================================
# 3. Main Interactive UI Application
# ========================================================
if db_conn:
    st.success("🎉 RxShield Engine Secured & Connected Successfully.")
    
    tab1, tab2, tab3 = st.tabs([
        "🔍 Smart Single Drug Search", 
        "⚔️ Drug-Drug Checker (Pair)", 
        "🥦 Drug-Food Warnings"
    ])
    
    # --- TAB 1: SMART SINGLE DRUG SEARCH ---
    with tab1:
        st.subheader("Comprehensive Drug Profile Lookup")
        selected_drug_profile = st.selectbox(
            "Select or Type a Drug Name:", 
            options=[""] + sorted_drugs_list, 
            index=0,
            key="profile_select"
        )
        
        if selected_drug_profile:
            # استخراج الـ ID من بين الأقواس
            target_id = selected_drug_profile.split('(')[-1].replace(')', '').strip().upper()
            current_drug_name = selected_drug_profile.split('(')[0].strip()
            
            query = "SELECT * FROM interactions WHERE \"Drug1 ID\" = ? OR \"Drug2 ID\" = ?"
            df_res = pd.read_sql_query(query, db_conn, params=(target_id, target_id))
            
            if not df_res.empty:
                # مصفوفة لتجهيز البيانات للعرض النظيف
                processed_data = []
                for _, row in df_res.iterrows():
                    d1_id = str(row['Drug1 ID']).upper()
                    d2_id = str(row['Drug2 ID']).upper()
                    
                    # معرفة اسم الدواء المقابل المكتشف
                    other_id = d2_id if d1_id == target_id else d1_id
                    other_name = name_to_id_map.get(other_id, "Unknown Drug")
                    
                    raw_text = row['Interaction']
                    clean_text = clean_interaction_text(raw_text, current_drug_name, other_name)
                    severity = get_severity_color(clean_text)
                    
                    processed_data.append({
                        "Interacting Drug": f"{other_name} ({other_id})",
                        "Clinical Severity": severity,
                        "Medical Description / Effect": clean_text
                    })
                
                df_clean = pd.DataFrame(processed_data)
                
                # إحصائيات سريعة
                c1, c2 = st.columns(2)
                c1.metric(f"Total Interactions for {current_drug_name}", len(df_clean))
                
                st.dataframe(df_clean, use_container_width=True, hide_index=True)
            else:
                st.warning(f"No clinical interactions registered for {selected_drug_profile}.")

    # --- TAB 2: DRUG VS DRUG CHECKER ---
    with tab2:
        st.subheader("Cross-Match Two Specific Medications")
        col1, col2 = st.columns(2)
        with col1:
            drug_selection_a = st.selectbox("Medication A:", options=[""] + sorted_drugs_list, key="sel_a")
        with col2:
            drug_selection_b = st.selectbox("Medication B:", options=[""] + sorted_drugs_list, key="sel_b")
            
        if drug_selection_a and drug_selection_b:
            id_a = drug_selection_a.split('(')[-1].replace(')', '').strip().upper()
            id_b = drug_selection_b.split('(')[-1].replace(')', '').strip().upper()
            name_a = drug_selection_a.split('(')[0].strip()
            name_b = drug_selection_b.split('(')[0].strip()
            
            if id_a == id_b:
                st.warning("Please select two different medications to check for cross-interaction.")
            else:
                query = """
                SELECT * FROM interactions 
                WHERE (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?) 
                   OR (\"Drug1 ID\" = ? AND \"Drug2 ID\" = ?)
                """
                df_pair = pd.read_sql_query(query, db_conn, params=(id_a, id_b, id_b, id_a))
                
                if not df_pair.empty:
                    raw_interaction = df_pair.iloc[0]['Interaction']
                    cleaned_interaction = clean_interaction_text(raw_interaction, name_a, name_b)
                    severity_status = get_severity_color(cleaned_interaction)
                    
                    st.error("⚠️ Clinical Interaction Alert Detected!")
                    
                    # إظهار التنبيه ملون حسب الخطورة بطريقة رائعة
                    if "🔴" in severity_status:
                        st.markdown(f"🚨 **Severity:** {severity_status}")
                        st.markdown(f"🛑 **Clinical Effect:** {cleaned_interaction}")
                    elif " An" in severity_status or "🟡" in severity_status:
                        st.markdown(f"⚠️ **Severity:** {severity_status}")
                        st.markdown(f"🔸 **Clinical Effect:** {cleaned_interaction}")
                else:
                    st.success(f"✅ **Safe Combination:** No direct clinical interaction found between {name_a} and {name_b} in the system.")

    # --- TAB 3: DRUG-FOOD INTERACTIONS ---
    with tab3:
        st.subheader("Dietary & Lifestyle Warnings")
        food_search = st.text_input("Type a medication name to find food interactions:", placeholder="e.g., Alcohol, Grapefruit, Warfarin").strip()
        
        if food_search and food_interactions_text:
            matching_lines = [line.strip() for line in food_interactions_text.split('\n') if food_search.lower() in line.lower()]
            if matching_lines:
                st.warning(f"Found {len(matching_lines)} dietary precautions:")
                for line in matching_lines[:15]:
                    st.markdown(f"💡 {line}")
            else:
                st.success("No critical dietary conflicts found for this entry.")
        elif not food_interactions_text:
            st.info("Dietary interactions ledger is currently offline.")
        else:
            st.info("Enter a substance name above to unlock nutritional compatibility checks.")

else:
    st.error("⚙️ Connection error.")
