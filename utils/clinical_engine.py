import re
import streamlit as st

# Import pre-compiled regex objects, rules, and the new organ system classifier
from utils.clinical_patterns import *
from utils.clinical_rules import *
from utils.clinical_knowledge import CLINICAL_EFFECTS
from utils.clinical_classifier import classify_organ_system

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

def lookup_clinical_knowledge(text):
    """
    Scans text against the centralized clinical knowledge base.
    """
    lower = text.lower()
    for keyword, data in CLINICAL_EFFECTS.items():
        if keyword in lower:
            return data
    return None

def extract_clinical_effect(raw_text: str):
    """
    Extract the primary clinical effect from an interaction sentence.
    Returns:
        (effect, confidence)
    """
    text = raw_text.strip()

    # Pre-compiled regex patterns coupled with text generation templates
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

    # Fallback to structural keyword maps for deterministic scoring
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

    # Check against centralized clinical knowledge base
    knowledge = lookup_clinical_knowledge(text)
    if knowledge:
        return knowledge["effect"], 0.96

    return "Unspecified pharmacological interaction", 0.50

def get_clinical_rules(severity):
    """
    Fetches the appropriate medical recommendation and monitoring guidelines based on severity.
    """
    if "🟥" in severity:
        return HIGH_RULES

    if "🟨" in severity:
        return MODERATE_RULES

    return LOW_RULES

def parse_clinical_details(raw_text, severity):
    """
    Deconstructs unstructured clinical database text into deterministic decision support fields.
    """
    # Extract clinical effect and algorithmic confidence
    effect, confidence = extract_clinical_effect(raw_text)
    
    # Classify the affected organ system using our new classifier
    organ_system = classify_organ_system(raw_text)
    
    # Fetch dynamically loaded rules
    rules = get_clinical_rules(severity)
    
    rec = rules["recommendation"]
    mon = rules["monitoring"]
    
    # Assign enterprise UI color codes
    if "🟥" in severity:
        color_code = "#d32f2f"
    elif "🟨" in severity:
        color_code = "#f57f17"
    else:
        color_code = "#1565c0"
        
    return effect, rec, mon, color_code, confidence, organ_system

def render_interaction_card(drug_pair, severity, mechanism_text):
    """
    Injects enterprise medical CSS styling templates into Streamlit to render highly scannable cards.
    """
    # Parse data including the new organ system parameter
    effect, rec, mon, color, confidence, organ_system = parse_clinical_details(mechanism_text, severity)
    
    st.markdown(f"""
        <div class="med-card interaction-detail" style="border-left: 6px solid {color}; padding: 18px 24px;">
            <h3 style="color: {color}; margin-top: 0; margin-bottom: 15px; font-size: 1.25rem;">{severity}</h3>
            <p><strong>💊 Interaction:</strong> {drug_pair}</p>
            <p><strong>🩺 Clinical Effect:</strong> {effect}</p>
            <p><strong>🎯 Extraction Confidence:</strong> {confidence:.0%}</p>
            <p><strong>🫀 Organ System:</strong> {organ_system}</p>
            <p><strong>📝 Recommendation:</strong> {rec}</p>
            <p><strong>⚙️ Mechanism:</strong> {mechanism_text}</p>
            <p><strong>🔍 Monitoring:</strong> {mon}</p>
        </div>
    """, unsafe_allow_html=True)
