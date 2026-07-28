CATEGORY_MAP = {

    "Pharmacodynamic": [
        "bleeding",
        "hemorrhage",
        "arrhythmia",
        "qtc",
        "hypoglycemia",
        "hyperkalemia",
        "sedation",
        "serotonin",
        "blood pressure"
    ],

    "Pharmacokinetic": [
        "metabolism",
        "serum concentration",
        "excretion",
        "absorption",
        "bioavailability",
        "cyp",
        "clearance"
    ],

    "Toxicity": [
        "toxicity",
        "hepatotoxicity",
        "nephrotoxicity",
        "ototoxicity"
    ],

    "Therapeutic Failure": [
        "therapeutic efficacy",
        "reduced efficacy",
        "decreased efficacy"
    ]
}


def classify_interaction_category(text):

    lower = text.lower()

    for category, keywords in CATEGORY_MAP.items():

        if any(word in lower for word in keywords):

            return category

    return "General Interaction"
