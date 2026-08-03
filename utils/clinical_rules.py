# utils/clinical_rules.py

RULES = [
    {
        "keywords": [
            "bleeding",
            "hemorrhage",
            "blood loss",
            "gastrointestinal bleeding"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Combined anticoagulant/antiplatelet effects increase bleeding risk.",
        "recommendation": "Avoid combination whenever possible. If necessary, monitor INR closely.",
        "monitoring": "Monitor INR, CBC, hemoglobin, hematocrit, and signs of bleeding."
    },
    {
        "keywords": [
            "arrhythmia",
            "cardiac arrhythmia",
            "ventricular arrhythmia"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Additive cardiotoxic effects may trigger arrhythmias.",
        "recommendation": "Avoid concomitant use or monitor ECG carefully.",
        "monitoring": "ECG, heart rate, electrolytes."
    },
    {
        "keywords": [
            "qtc prolongation",
            "qtc",
            "torsade",
            "torsades de pointes"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Combined QT prolongation may induce Torsades de Pointes.",
        "recommendation": "Avoid combination or perform ECG monitoring.",
        "monitoring": "ECG and electrolyte monitoring."
    },
    {
        "keywords": [
            "therapeutic efficacy",
            "decreased effectiveness",
            "diminished therapeutic effect"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "One drug alters the clinical effectiveness of the other.",
        "recommendation": "Dose adjustment may be required.",
        "monitoring": "Monitor therapeutic response."
    },
    {
        "keywords": [
            "serum concentration",
            "serum levels"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Pharmacokinetic interaction affecting serum levels.",
        "recommendation": "Monitor serum concentration when appropriate.",
        "monitoring": "Drug levels and adverse effects."
    },
    {
        "keywords": [
            "metabolism",
            "cyp modulation",
            "cyp3a4"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Interaction through CYP enzyme modulation.",
        "recommendation": "Monitor efficacy and toxicity.",
        "monitoring": "Clinical response and adverse reactions."
    },
    {
        "keywords": [
            "excretion",
            "renal elimination",
            "clearance"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Altered renal elimination.",
        "recommendation": "Dose adjustment may be necessary.",
        "monitoring": "Renal function."
    }
]
