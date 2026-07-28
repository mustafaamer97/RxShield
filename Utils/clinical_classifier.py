ORGAN_SYSTEMS = {

    "Cardiovascular": [
        "arrhythmia",
        "qtc",
        "blood pressure",
        "hypotension",
        "hypertension",
        "bradycardia",
        "tachycardia"
    ],

    "Renal": [
        "kidney",
        "renal",
        "creatinine",
        "egfr",
        "nephrotoxicity"
    ],

    "Hepatic": [
        "liver",
        "hepatic",
        "hepatotoxicity",
        "ast",
        "alt",
        "bilirubin"
    ],

    "Endocrine": [
        "hypoglycemia",
        "hyperglycemia",
        "glucose"
    ],

    "Neurologic": [
        "serotonin",
        "seizure",
        "cns",
        "sedation",
        "dizziness"
    ],

    "Hematologic": [
        "bleeding",
        "hemorrhage",
        "platelet",
        "inr"
    ],

    "Electrolytes": [
        "hyperkalemia",
        "hypokalemia",
        "potassium",
        "sodium"
    ]

}
def classify_organ_system(text):

    lower = text.lower()

    for system, keywords in ORGAN_SYSTEMS.items():

        if any(word in lower for word in keywords):

            return system

    return "General Pharmacology"
