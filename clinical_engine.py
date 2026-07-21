# ==========================================================
# RxShield Clinical Knowledge Base
# ==========================================================

clinical_rules = {

    # =========================
    # Major
    # =========================

    "anticoagulant": {
        "severity": "Major",
        "mechanism": "Pharmacodynamic",
        "evidence": "Excellent",
        "clinical_management":
            "Monitor INR closely. Assess for bleeding. Consider dose adjustment."
    },

    "bleeding": {
        "severity": "Major",
        "mechanism": "Pharmacodynamic",
        "evidence": "Excellent",
        "clinical_management":
            "Monitor for signs of bleeding. Avoid unnecessary NSAIDs."
    },

    "hemorrhage": {
        "severity": "Major",
        "mechanism": "Pharmacodynamic",
        "evidence": "Excellent",
        "clinical_management":
            "Immediate clinical monitoring is recommended."
    },

    "qt prolongation": {
        "severity": "Major",
        "mechanism": "Pharmacodynamic",
        "evidence": "Good",
        "clinical_management":
            "Monitor ECG. Avoid combination if possible."
    },

    "arrhythmogenic": {
        "severity": "Major",
        "mechanism": "Pharmacodynamic",
        "evidence": "Good",
        "clinical_management":
            "Monitor ECG and electrolytes."
    },

    "serotonin syndrome": {
        "severity": "Major",
        "mechanism": "Pharmacodynamic",
        "evidence": "Excellent",
        "clinical_management":
            "Avoid combination whenever possible."
    },

    # =========================
    # Moderate
    # =========================

    "cns depression": {
        "severity": "Moderate",
        "mechanism": "Pharmacodynamic",
        "evidence": "Good",
        "clinical_management":
            "Monitor sedation and respiratory status."
    },

    "hypoglycemia": {
        "severity": "Moderate",
        "mechanism": "Pharmacodynamic",
        "evidence": "Good",
        "clinical_management":
            "Monitor blood glucose frequently."
    },

    "hyperkalemia": {
        "severity": "Moderate",
        "mechanism": "Pharmacodynamic",
        "evidence": "Good",
        "clinical_management":
            "Monitor serum potassium."
    },

    # =========================
    # Minor
    # =========================

    "photosensitivity": {
        "severity": "Minor",
        "mechanism": "Unknown",
        "evidence": "Fair",
        "clinical_management":
            "Advise sun protection."
    },

    "dizziness": {
        "severity": "Minor",
        "mechanism": "Unknown",
        "evidence": "Fair",
        "clinical_management":
            "Use caution while driving."
    },

    "nausea": {
        "severity": "Minor",
        "mechanism": "Unknown",
        "evidence": "Fair",
        "clinical_management":
            "Take with food if appropriate."
    }

}

print("Clinical rules:", len(clinical_rules))# ==========================================================
# Base rules by Interaction Type
# ==========================================================

interaction_type_rules = {

    "Synergism": {
        "severity": "Moderate",
        "mechanism": "Pharmacodynamic",
        "evidence": "Good",
        "clinical_management":
            "Monitor patient response. Dose adjustment may be required."
    },

    "Antagonism": {
        "severity": "Moderate",
        "mechanism": "Pharmacodynamic",
        "evidence": "Good",
        "clinical_management":
            "Monitor therapeutic efficacy. Consider alternative therapy if needed."
    },

    "New Adverse": {
        "severity": "Major",
        "mechanism": "Unknown",
        "evidence": "Good",
        "clinical_management":
            "Monitor patient closely for newly reported adverse reactions."
    }

}

print(interaction_type_rules)def get_clinical_metadata(interaction_type, adverse_effect):

    # 1. نبدأ بالقواعد الأساسية حسب نوع التفاعل
    metadata = interaction_type_rules.get(
        interaction_type,
        {
            "severity": "Unknown",
            "mechanism": "Unknown",
            "evidence": "Unknown",
            "clinical_management": "No recommendation available."
        }
    ).copy()

    # 2. إذا وجد عرض جانبي معروف، فهو يغلب القاعدة الأساسية
    if adverse_effect:

        adverse = adverse_effect.lower()

        for keyword, rule in clinical_rules.items():

            if keyword in adverse:

                metadata.update(rule)
                break

    return metadata
