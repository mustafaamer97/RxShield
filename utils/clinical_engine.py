import re


def classify_severity(text):
    text = text.lower()

    critical = [
        "fatal",
        "bleeding",
        "hemorrhage",
        "arrhythmia",
        "qtc prolongation",
        "torsade",
        "cardiac arrest",
        "respiratory depression",
    ]

    moderate = [
        "therapeutic efficacy",
        "serum concentration",
        "metabolism",
        "excretion",
    ]

    for word in critical:
        if word in text:
            return "🔴 Critical"

    for word in moderate:
        if word in text:
            return "🟠 Moderate"

    return "🟢 Minor"


def build_report(interaction_text, drug1, drug2):

    text = interaction_text.replace("(.*)", "{}")
    text = text.format(drug1, drug2)

    severity = classify_severity(text)

    mechanism = "Pharmacodynamic interaction."

    recommendation = "Monitor clinically."

    monitoring = "Routine clinical monitoring."

    lower = text.lower()

    if "bleeding" in lower:

        mechanism = (
            "Combined anticoagulant/antiplatelet effects increase bleeding risk."
        )

        recommendation = (
            "Avoid combination whenever possible. "
            "If necessary, monitor INR closely."
        )

        monitoring = (
            "Monitor INR, CBC, hemoglobin, hematocrit and signs of bleeding."
        )

    elif "qtc" in lower:

        mechanism = (
            "Additive QT prolongation may predispose to ventricular arrhythmias."
        )

        recommendation = (
            "Avoid concomitant QT-prolonging agents whenever possible."
        )

        monitoring = (
            "Monitor ECG and serum potassium/magnesium."
        )

    elif "therapeutic efficacy" in lower:

        mechanism = (
            "One drug alters the pharmacological effectiveness of the other."
        )

        recommendation = (
            "Consider dose adjustment or alternative therapy."
        )

        monitoring = (
            "Assess therapeutic response."
        )

    elif "serum concentration" in lower:

        mechanism = (
            "Altered pharmacokinetics affecting systemic exposure."
        )

        recommendation = (
            "Dose adjustment may be required."
        )

        monitoring = (
            "Monitor serum drug concentrations if available."
        )

    return {
        "severity": severity,
        "interaction": text,
        "mechanism": mechanism,
        "recommendation": recommendation,
        "monitoring": monitoring,
    }
