import re
import streamlit as st

from utils.clinical_patterns import *
from utils.clinical_rules import *
from utils.clinical_knowledge import CLINICAL_EFFECTS
from utils.clinical_classifier import classify_organ_system

def clean_interaction_text(text, drug1_name, drug2_name=None):
    if not text: 
        return ""
    if drug2_name is None: 
        drug2_name = drug1_name
        
    counter = [0]
    def replace_placeholder(match):
        counter[0] += 1
        return f" {drug1_name} " if counter[0] == 1 else f" {drug2_name} "
        
    cleaned = re.sub(r'\(\.\*\)', replace_placeholder, str(text))
    cleaned = cleaned.replace("the risk or severity of", "The risk of")
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned + '.' if cleaned and not cleaned.endswith('.') else cleaned

def get_severity_color(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["bleeding", "arrhythmia", "qtc prolongation", "toxicity", "fatal", "severe", "hemorrhage"]):
        return "🟥 HIGH RISK"
    elif any(w in text_lower for w in ["decrease the therapeutic efficacy", "increase the excretion rate", "risk of adverse effects"]):
        return "🟨 MODERATE CAUTION"
    return "🟦 MONITOR / INFO"

def lookup_clinical_knowledge(text):
    lower = text.lower()
    for keyword, data in CLINICAL_EFFECTS.items():
        if keyword in lower:
            return data
    return None

def extract_clinical_effect(raw_text: str):
    text = raw_text.strip()
    patterns = [
        (RISK_PATTERN, "Increased risk of {}"),
        (SERUM_PATTERN, "Altered serum concentration of {}"),
        (METABOLISM_PATTERN, "Altered metabolism of {}"),
        (EXCRETION_PATTERN, "Altered excretion of {}"),
        (THERAPEUTIC_PATTERN, "Reduced therapeutic efficacy of {}"),
    ]
    for pattern, template in patterns:
        match = pattern.search(text)
        if match:
            return template.format(match.group(1).strip()), 0.98

    lower = text.lower()
    keyword_map = {
        "hypoglycemia": "Increased risk of hypoglycemia",
        "hyperkalemia": "Increased risk of hyperkalemia",
        "bleeding": "Increased bleeding risk",
        "hemorrhage": "Increased bleeding risk",
        "toxicity": "Drug toxicity",
        "arrhythmia": "Cardiac arrhythmia",
        "qtc prolongation": "QT prolongation",
    }
    for keyword, result in keyword_map.items():
        if keyword in lower:
            return result, 0.90

    knowledge = lookup_clinical_knowledge(text)
    if knowledge:
        return knowledge["effect"], 0.96

    return "Unspecified pharmacological interaction", 0.50

def get_clinical_rules(severity):
    if "🟥" in severity:
        return HIGH_RULES
    if "🟨" in severity:
        return MODERATE_RULES
    return LOW_RULES

def parse_clinical_details(raw_text, severity):
    effect, confidence = extract_clinical_effect(raw_text)
    organ_system = classify_organ_system(raw_text)
    rules = get_clinical_rules(severity)
    rec = rules["recommendation"]
    mon = rules["monitoring"]
    
    if "🟥" in severity:
        color_code = "#d32f2f"
    elif "🟨" in severity:
        color_code = "#f57f17"
    else:
        color_code = "#1565c0"
        
    return effect, rec, mon, color_code, confidence, organ_system

# ==========================================
# الدالة الجديدة التي طلبها تشات جي بي تي
# ==========================================
def analyze_interaction(drug1_name, drug2_name, cleaned_text):
    severity = get_severity_color(cleaned_text)
    effect, rec, mon, color, confidence, organ_system = parse_clinical_details(cleaned_text, severity)
    
    # إرجاع قاموس (Dictionary) يحتوي على كل التفاصيل
    return {
        "drug_pair": f"{drug1_name} + {drug2_name}",
        "severity": severity,
        "effect": effect,
        "confidence": confidence,
        "organ_system": organ_system,
        "recommendation": rec,
        "mechanism_text": cleaned_text,
        "monitoring": mon,
        "color": color
    }

# ==========================================
# تم تحديث هذه الدالة لتقبل القاموس (Result)
# ==========================================
def render_interaction_card(result):
    st.markdown(f"""
        <div class="med-card interaction-detail" style="border-left: 6px solid {result['color']}; padding: 18px 24px;">
            <h3 style="color: {result['color']}; margin-top: 0; margin-bottom: 15px; font-size: 1.25rem;">{result['severity']}</h3>
            <p><strong>💊 Interaction:</strong> {result['drug_pair']}</p>
            <p><strong>🩺 Clinical Effect:</strong> {result['effect']}</p>
            <p><strong>🎯 Extraction Confidence:</strong> {result['confidence']:.0%}</p>
            <p><strong>🫀 Organ System:</strong> {result['organ_system']}</p>
            <p><strong>📝 Recommendation:</strong> {result['recommendation']}</p>
            <p><strong>⚙️ Mechanism:</strong> {result['mechanism_text']}</p>
            <p><strong>🔍 Monitoring:</strong> {result['monitoring']}</p>
        </div>
    """, unsafe_allow_html=True)
