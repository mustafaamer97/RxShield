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
        "mechanism": "Combined anticoagulant/antiplatelet effects increase bleeding risk and susceptibility to severe hemorrhage.",
        "recommendation": "Avoid combination whenever possible. Monitor INR closely.",
        "monitoring": "Monitor INR, CBC, hemoglobin, hematocrit, and signs of bleeding/hemorrhage."
    },
    {
        "keywords": [
            "arrhythmia",
            "cardiac arrhythmia",
            "ventricular arrhythmia"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Additive cardiotoxic effects.",
        "recommendation": "Avoid combination if possible or monitor ECG carefully.",
        "monitoring": "ECG, heart rate, and electrolytes."
    },
    {
        "keywords": [
            "qtc prolongation",
            "qtc",
            "torsade",
            "torsades de pointes"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Additive QT prolongation may trigger drug-induced ventricular arrhythmia (Torsades de Pointes).",
        "recommendation": "Avoid coadministration. Immediate review of therapy if suspected.",
        "monitoring": "Continuous or baseline ECG, serum potassium, and magnesium."
    },
    {
        "keywords": [
            "cns depression",
            "sedation",
            "somnolence"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Additive central nervous system depression.",
        "recommendation": "Avoid combined sedatives whenever possible.",
        "monitoring": "Respiratory rate, oxygen saturation, and mental status."
    },
    {
        "keywords": [
            "serotonin syndrome",
            "serotonergic"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Excess serotonergic activity.",
        "recommendation": "Discontinue serotonergic agents immediately if suspected.",
        "monitoring": "Mental status, body temperature, blood pressure, and clonus."
    },
    {
        "keywords": [
            "nephrotoxicity",
            "renal toxicity",
            "kidney injury"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Additive renal toxicity.",
        "recommendation": "Avoid nephrotoxic combinations.",
        "monitoring": "Serum creatinine, eGFR, and fluid balance."
    },
    {
        "keywords": [
            "hepatotoxicity",
            "liver injury",
            "hepatic impairment"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Drug-induced liver injury.",
        "recommendation": "Avoid hepatotoxic combinations.",
        "monitoring": "Liver function tests (ALT, AST, bilirubin, alkaline phosphatase)."
    },
    {
        "keywords": [
            "rhabdomyolysis",
            "myopathy",
            "muscle toxicity"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Drug-induced muscle toxicity ranging from myopathy to severe skeletal muscle injury (Rhabdomyolysis).",
        "recommendation": "Discontinue therapy immediately if severe; consider alternative therapy for mild cases.",
        "monitoring": "Creatine Kinase (CK) levels and renal function."
    },
    {
        "keywords": [
            "hyperkalemia",
            "elevated potassium"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Potassium accumulation.",
        "recommendation": "Avoid multiple potassium-elevating drugs.",
        "monitoring": "Serum potassium levels."
    },
    {
        "keywords": [
            "hypoglycemia",
            "low blood glucose"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Enhanced glucose-lowering effect.",
        "recommendation": "Adjust antidiabetic dose if required.",
        "monitoring": "Blood glucose monitoring."
    },
    {
        "keywords": [
            "therapeutic efficacy",
            "decreased effectiveness",
            "diminished therapeutic effect"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Reduced pharmacological effect or clinical effectiveness.",
        "recommendation": "Consider dose adjustment or alternative agents.",
        "monitoring": "Clinical therapeutic response."
    },
    {
        "keywords": [
            "serum concentration",
            "serum levels",
            "metabolism",
            "excretion",
            "cyp modulation"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Pharmacokinetic interaction affecting drug metabolism, excretion, or systemic exposure.",
        "recommendation": "Dose adjustment may be required.",
        "monitoring": "Serum drug levels if available, along with monitoring for toxicity."
    }
]
