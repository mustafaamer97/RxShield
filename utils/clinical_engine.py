import re


def clean_interaction_text(text, drug1_name, drug2_name):
    """
    Replace DrugBank placeholders (.*) with actual drug names.
    """

    if not text:
        return ""

    count = 0

    def replace(_):
        nonlocal count
        count += 1

        if count == 1:
            return drug1_name

        return drug2_name

    text = re.sub(r"\(\.\*\)", replace, text)

    text = text.strip()

    if not text.endswith("."):
        text += "."

    return text


def get_severity(text):
    """
    Estimate severity from interaction text.
    """

    if not text:
        return "Unknown"

    text = text.lower()

    critical = [
        "fatal",
        "hemorrhage",
        "bleeding",
        "arrhythmia",
        "qtc prolongation",
        "torsade",
    ]

    high = [
        "toxicit",
        "cns depression",
        "respiratory depression",
        "serotonin syndrome",
    ]

    moderate = [
        "decrease the therapeutic efficacy",
        "increase the excretion rate",
        "lower serum level",
    ]

    for word in critical:
        if word in text:
            return "Critical"

    for word in high:
        if word in text:
            return "High"

    for word in moderate:
        if word in text:
            return "Moderate"

    return "Monitor"


def build_report(interaction_text, drug1_name, drug2_name):
    """
    Build a structured clinical report.
    """

    clean_text = clean_interaction_text(
        interaction_text,
        drug1_name,
        drug2_name,
    )

    severity = get_severity(clean_text)

    return {
        "severity": severity,
        "interaction": clean_text,
    }
