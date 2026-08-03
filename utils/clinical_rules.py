RULES = [

    {
        "keyword": "bleeding",
        "severity": "🔴 Critical",
        "mechanism": "Combined anticoagulant and/or antiplatelet effects increase the risk of bleeding.",
        "recommendation": "Avoid combination whenever possible. If unavoidable, monitor INR closely and consider dose adjustment.",
        "monitoring": "INR, CBC, Hemoglobin, Hematocrit, signs of bleeding."
    },

    {
        "keyword": "hemorrhage",
        "severity": "🔴 Critical",
        "mechanism": "Marked increase in hemorrhagic risk due to additive pharmacodynamic effects.",
        "recommendation": "Avoid combination whenever possible.",
        "monitoring": "CBC, Hemoglobin, clinical bleeding."
    },

    {
        "keyword": "qtc prolongation",
        "severity": "🔴 Critical",
        "mechanism": "Additive QT prolongation may precipitate ventricular arrhythmias.",
        "recommendation": "Avoid concomitant QT-prolonging medications.",
        "monitoring": "ECG, Potassium, Magnesium."
    },

    {
        "keyword": "arrhythmia",
        "severity": "🔴 Critical",
        "mechanism": "Combined electrophysiologic effects increase arrhythmia risk.",
        "recommendation": "Use alternative therapy when feasible.",
        "monitoring": "ECG and cardiac monitoring."
    },

    {
        "keyword": "cns depression",
        "severity": "🟠 Moderate",
        "mechanism": "Additive central nervous system depressant effects.",
        "recommendation": "Reduce dose if needed and avoid alcohol.",
        "monitoring": "Mental status and respiratory function."
    },

    {
        "keyword": "therapeutic efficacy",
        "severity": "🟠 Moderate",
        "mechanism": "One drug reduces the pharmacologic effect of the other.",
        "recommendation": "Consider dose adjustment or an alternative therapy.",
        "monitoring": "Clinical response."
    },

    {
        "keyword": "serum concentration",
        "severity": "🟠 Moderate",
        "mechanism": "Altered pharmacokinetics affecting drug exposure.",
        "recommendation": "Dose adjustment may be required.",
        "monitoring": "Drug serum concentrations if available."
    },

    {
        "keyword": "metabolism",
        "severity": "🟠 Moderate",
        "mechanism": "Drug metabolism may be inhibited or induced.",
        "recommendation": "Review metabolic pathway and adjust dose if required.",
        "monitoring": "Clinical efficacy and adverse effects."
    },

    {
        "keyword": "excretion",
        "severity": "🟠 Moderate",
        "mechanism": "Altered renal elimination changes drug exposure.",
        "recommendation": "Monitor renal function.",
        "monitoring": "Renal function and therapeutic response."
    },

]
