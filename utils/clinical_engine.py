import re


def classify_severity(text: str):
    text = text.lower()

    critical = [
        "fatal",
        "hemorrhage",
        "bleeding",
        "arrhythmia",
        "qtc prolongation",
        "torsade",
        "cardiac arrest",
        "respiratory depression"
    ]

    moderate = [
        "increase serum concentration",
        "decrease serum concentration",
        "therapeutic efficacy",
        "metabolism",
        "excretion"
    ]

    for word in critical:
        if word in text:
            return "🔴 Critical"

    for word in moderate:
        if word in text:
            return "🟠 Moderate"

    return "🟢 Minor"


def build_report(interaction_text, drug1, drug2):

    sentence = interaction_text.replace("(.*)", "{}")
    sentence = sentence.format(drug1, drug2)

    severity = classify_severity(sentence)

    recommendation = "Monitor patient clinically."

    if "bleeding" in sentence.lower():
        recommendation = (
            "Avoid combination when possible. "
            "Monitor INR and signs of bleeding."
        )

    elif "qtc" in sentence.lower():
        recommendation = (
            "Monitor ECG and avoid other QT-prolonging drugs."
        )

    elif "therapeutic efficacy" in sentence.lower():
        recommendation = (
            "Dose adjustment may be required."
        )

    return {
        "severity": severity,
        "interaction": sentence,
        "recommendation": recommendation
    }
