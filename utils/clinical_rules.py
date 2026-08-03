# utils/clinical_rules.py

RULES = [
    # ==========================================
    # CRITICAL RULES (🔴 Critical)
    # ==========================================
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
            "somnolence",
            "cns depressant"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Additive central nervous system depression.",
        "recommendation": "Avoid combined sedatives whenever possible.",
        "monitoring": "Respiratory rate, oxygen saturation, and mental status."
    },
    {
        "keywords": [
            "serotonin syndrome",
            "serotonergic",
            "serotonin"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Excess serotonergic activity and stimulation.",
        "recommendation": "Discontinue serotonergic agents immediately if suspected.",
        "monitoring": "Mental status, body temperature, blood pressure, and clonus."
    },
    {
        "keywords": [
            "nephrotoxicity",
            "renal toxicity",
            "kidney injury",
            "acute kidney injury"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Additive nephrotoxic effects.",
        "recommendation": "Avoid prolonged co-administration.",
        "monitoring": "Serum creatinine (SCr), eGFR, and fluid balance/urine output."
    },
    {
        "keywords": [
            "hepatotoxicity",
            "liver injury",
            "hepatic impairment",
            "hepatic toxicity"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Drug-induced liver injury / Additive hepatic toxicity.",
        "recommendation": "Avoid hepatotoxic combinations or monitor closely.",
        "monitoring": "Liver function tests (ALT, AST, bilirubin, alkaline phosphatase)."
    },
    {
        "keywords": [
            "rhabdomyolysis",
            "myopathy",
            "muscle toxicity"
        ],
        "severity": "🔴 Critical",
        "mechanism": "Drug-induced muscle toxicity ranging from myopathy to severe skeletal muscle injury (Rhabdomyolysis) due to marked increase in exposure.",
        "recommendation": "Discontinue therapy immediately if severe; consider alternative therapy for mild cases.",
        "monitoring": "Creatine Kinase (CK) levels and renal function."
    },
    
    # ==========================================
    # CYP ENZYMES & PHARMACOKINETICS (🔴 Critical)
    # ==========================================
    {
        "keywords": ["cyp3a4", "cyp2d6", "cyp2c9", "cyp2c19"],
        "severity": "🔴 Critical",
        "mechanism": "Cytochrome P450 enzyme inhibition decreases drug metabolism causing elevated plasma concentration and potential toxicity.",
        "recommendation": "Avoid combination or adjust dose significantly.",
        "monitoring": "Monitor toxicity, liver function, and ECG when applicable."
    },

    # ==========================================
    # MODERATE RULES (🟠 Moderate)
    # ==========================================
    {
        "keywords": [
            "hyperkalemia",
            "elevated potassium"
        ],
        "severity": "🟠 Moderate",
        "mechanism": "Potassium accumulation due to additive potassium retention.",
        "recommendation": "Avoid multiple potassium-elevating drugs.",
        "monitoring": "Serum potassium levels and renal function."
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
        "mechanism": "Pharmacokinetic interaction affecting drug metabolism, excretion, or systemic exposure via enzyme modulation.",
        "recommendation": "Dose adjustment may be required.",
        "monitoring": "Monitor therapeutic response, serum drug levels if available, and adverse effects."
    }
]
