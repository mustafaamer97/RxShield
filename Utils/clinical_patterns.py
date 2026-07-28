import re
import streamlit as st

# Import all pre-compiled regex objects from your clinical patterns file
from utils.clinical_patterns import *

def clean_interaction_text(text, drug1_name, drug2_name=None):
    """
    Cleans raw medical text and maps drug placeholders accurately to prevent string repetition.
    """
    if not text: 
        return ""
    if drug2_name is None: 
        drug2_name = drug1_name
        
    counter = [0]
    def replace_placeholder(match):
        counter[0] += 1
        return f" {drug1_name} " if counter[0] == 1 else f" {drug2_name} "
        
    cleaned = re.sub(r'\(\.\*\)', replace_placeholder, text)
    cleaned = cleaned.replace("the risk or severity of", "The risk of")
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned + '.' if cleaned and not cleaned.endswith('.') else cleaned

def get_severity_color(text):
    """
    Evaluates interaction clinical text vectors to assign appropriate risk severity levels.
    """
    text_lower = text.lower()
    if any(w in text_lower for w in ["bleeding", "arrhythmia", "qtc prolongation", "toxicity", "fatal", "severe", "hemorrhage"]):
        return "🟥 HIGH RISK"
    elif any(w in text_lower for w in ["decrease the therapeutic efficacy", "increase the excretion rate", "risk of adverse effects"]):
        return "🟨 MODERATE CAUTION"
    return "🟦 MONITOR / INFO"

def parse_clinical_details(raw_text, severity):
    """
    Brain parsing engine that handles structural decomposition of unstructured medical text blocks.
    """
    effect = "Unspecified pharmacological interaction"
    
    # Utilizing pre-compiled pattern matchers for optimized engine throughput
    match_risk = RISK_PATTERN.search(raw_text)
    match_conc = SERUM_PATTERN.search(raw_text)
    match_metab = METABOLISM_PATTERN.search(raw_text)
    
    # Conditional branching for structural breakdown alignment
    if match_risk: 
        effect = f"Increased risk of {match_risk.group(1).strip()}"
    elif match_conc: 
        effect = f"Altered serum concentration ({match_conc.group(1).strip()})"
    elif match_metab: 
        effect = f"Altered metabolism ({match_metab.group(1).strip()})"
    elif "decrease the therapeutic efficacy" in raw_text.lower(): 
        effect = "Decreased therapeutic efficacy"
    elif "increase the excretion rate" in raw_text.lower(): 
        effect = "Increased excretion rate (Reduced efficacy)"
    
    # Formatting capitalization across safety outputs
    effect = effect[0].upper() + effect[1:] if effect else effect
    
    # Rule-bound deterministic logic for handling localized advisory components
    if "🟥" in severity:
        rec = "Consider alternative therapy. If co-administration is strictly necessary, dose adjustment is mandatory."
        mon = "Continuous and rigorous monitoring for signs of clinical toxicity and adverse events."
        color_code = "#d32f2f"
    elif "🟨" in severity:
        rec = "Evaluate risk vs. benefit. Adjust dosages of one or both agents if needed."
        mon = "Regular monitoring of patient vitals and specific laboratory parameters."
        color_code = "#f57f17"
    else:
        rec = "No immediate therapy modification typically required. Use standard clinical judgment."
        mon = "Standard clinical observation."
        color_code = "#1565c0"
        
    return effect, rec, mon, color_code

def render_interaction_card(drug_pair, severity, mechanism_text):
    """
    Injects enterprise medical CSS styling templates to isolate distinct clinical indices clearly.
    """
    effect, rec, mon, color = parse_clinical_details(mechanism_text, severity)
    
    st.markdown(f"""
        <div class="med-card interaction-detail" style="border-left: 6px solid {color}; padding: 18px 24px;">
            <h3 style="color: {color}; margin-top: 0; margin-bottom: 15px; font-size: 1.25rem;">{severity}</h3>
            <p><strong>💊 Interaction:</strong> {drug_pair}</p>
            <p><strong>🩺 Clinical Effect:</strong> {effect}</p>
            <p><strong>📝 Recommendation:</strong> {rec}</p>
            <p><strong>⚙️ Mechanism:</strong> {mechanism_text}</p>
            <p><strong>🔍 Monitoring:</strong> {mon}</p>
        </div>
    """, unsafe_allow_html=True)
import re
import streamlit as st

# Import all pre-compiled regex objects from your clinical patterns file
from utils.clinical_patterns import *

def clean_interaction_text(text, drug1_name, drug2_name=None):
    """
    Cleans raw medical text and maps drug placeholders accurately to prevent string repetition.
    """
    if not text: 
        return ""
    if drug2_name is None: 
        drug2_name = drug1_name
        
    counter = [0]
    def replace_placeholder(match):
        counter[0] += 1
        return f" {drug1_name} " if counter[0] == 1 else f" {drug2_name} "
        
    cleaned = re.sub(r'\(\.\*\)', replace_placeholder, text)
    cleaned = cleaned.replace("the risk or severity of", "The risk of")
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned + '.' if cleaned and not cleaned.endswith('.') else cleaned

def get_severity_color(text):
    """
    Evaluates interaction clinical text vectors to assign appropriate risk severity levels.
    """
    text_lower = text.lower()
    if any(w in text_lower for w in ["bleeding", "arrhythmia", "qtc prolongation", "toxicity", "fatal", "severe", "hemorrhage"]):
        return "🟥 HIGH RISK"
    elif any(w in text_lower for w in ["decrease the therapeutic efficacy", "increase the excretion rate", "risk of adverse effects"]):
        return "🟨 MODERATE CAUTION"
    return "🟦 MONITOR / INFO"

def extract_clinical_effect(raw_text: str):
    """
    Extract the primary clinical effect from an interaction sentence.
    Returns:
        (effect, confidence)
    """
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

    return "Unspecified pharmacological interaction", 0.50

def parse_clinical_details(raw_text, severity):
    """
    Brain parsing engine that handles structural decomposition of unstructured medical text blocks.
    """
    # Extract clinical findings and confidence using the dedicated extraction flow
    effect, confidence = extract_clinical_effect(raw_text)
    
    # Rule-bound deterministic logic for handling localized advisory components
    if "🟥" in severity:
        rec = "Consider alternative therapy. If co-administration is strictly necessary, dose adjustment is mandatory."
        mon = "Continuous and rigorous monitoring for signs of clinical toxicity and adverse events."
        color_code = "#d32f2f"
    elif "🟨" in severity:
        rec = "Evaluate risk vs. benefit. Adjust dosages of one or both agents if needed."
        mon = "Regular monitoring of patient vitals and specific laboratory parameters."
        color_code = "#f57f17"
    else:
        rec = "No immediate therapy modification typically required. Use standard clinical judgment."
        mon = "Standard clinical observation."
        color_code = "#1565c0"
        
    return effect, rec, mon, color_code, confidence

def render_interaction_card(drug_pair, severity, mechanism_text):
    """
    Injects enterprise medical CSS styling templates to isolate distinct clinical indices clearly.
    """
    effect, rec, mon, color, confidence = parse_clinical_details(mechanism_text, severity)
    
    st.markdown(f"""
        <div class="med-card interaction-detail" style="border-left: 6px solid {color}; padding: 18px 24px;">
            <h3 style="color: {color}; margin-top: 0; margin-bottom: 15px; font-size: 1.25rem;">{severity}</h3>
            <p><strong>💊 Interaction:</strong> {drug_pair}</p>
            <p><strong>🩺 Clinical Effect:</strong> {effect}</p>
            <p><strong>🎯 Extraction Confidence:</strong> {confidence:.0%}</p>
            <p><strong>📝 Recommendation:</strong> {rec}</p>
            <p><strong>⚙️ Mechanism:</strong> {mechanism_text}</p>
            <p><strong>🔍 Monitoring:</strong> {mon}</p>
        </div>
    """, unsafe_allow_html=True)








