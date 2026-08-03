RULES = [

    {
        "keyword": "bleeding",
        "severity": "🔴 Critical",
        "mechanism": "Combined anticoagulant/antiplatelet effects increase bleeding risk.",
        "recommendation": "Avoid combination whenever possible. If necessary, monitor INR closely.",
        "monitoring": "Monitor INR, CBC, hemoglobin, hematocrit, and signs of bleeding."
    },

    {
        "keyword": "hemorrhage",
        "severity": "🔴 Critical",
        "mechanism": "Increased risk of severe hemorrhage.",
        "recommendation": "Avoid combination whenever possible.",
        "monitoring": "Monitor for any evidence of internal or external bleeding."
    },

    {
        "keyword": "arrhythmia",
        "severity": "🔴 Critical",
        "mechanism": "Additive cardiotoxic effects may trigger arrhythmias.",
        "recommendation": "Avoid concomitant use or monitor ECG carefully.",
        "monitoring": "ECG, heart rate, electrolytes."
    },

    {
        "keyword": "qtc prolongation",
        "severity": "🔴 Critical",
        "mechanism": "Combined QT prolongation may induce Torsades de Pointes.",
        "recommendation": "Avoid combination or perform ECG monitoring.",
        "monitoring": "ECG and electrolyte monitoring."
    },

    {
        "keyword": "therapeutic efficacy",
        "severity": "🟠 Moderate",
        "mechanism": "One drug alters the clinical effectiveness of the other.",
        "recommendation": "Dose adjustment may be required.",
        "monitoring": "Monitor therapeutic response."
    },

    {
        "keyword": "serum concentration",
        "severity": "🟠 Moderate",
        "mechanism": "Pharmacokinetic interaction affecting serum levels.",
        "recommendation": "Monitor serum concentration when appropriate.",
        "monitoring": "Drug levels and adverse effects."
    },

    {
        "keyword": "metabolism",
        "severity": "🟠 Moderate",
        "mechanism": "Interaction through CYP enzyme modulation.",
        "recommendation": "Monitor efficacy and toxicity.",
        "monitoring": "Clinical response and adverse reactions."
    },

    {
        "keyword": "excretion",
        "severity": "🟠 Moderate",
        "mechanism": "Altered renal elimination.",
        "recommendation": "Dose adjustment may be necessary.",
        "monitoring": "Renal function."
    }

]
