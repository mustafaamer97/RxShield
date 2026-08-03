import re
from utils.clinical_rules import RULES


def find_rule(text):
    """
    يبحث عن القاعدة الطبية المطابقة للنص بناءً على الكلمات المفتاحية (Keywords).
    إذا لم يعثر على تطابق، يرجع قاموساً افتراضياً للحالات البسيطة.
    """
    lower = text.lower()

    for rule in RULES:
        if rule["keyword"] in lower:
            return rule

    return {
        "severity": "🟢 Minor",
        "mechanism": "Unknown mechanism.",
        "recommendation": "Clinical monitoring.",
        "monitoring": "Routine monitoring.",
    }


def classify_severity(text):
    """
    يصنف خطورة التفاعل كخيار احتياطي (Fallback) أو تصنيف سريع.
    ملاحظة: دالة find_rule الآن تقوم بجلب الخطورة مباشرة من القواعد، 
    ولكن تم الاحتفاظ بهذه الدالة للحفاظ على التوافق البرمجي.
    """
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
    """
    يبني التقرير السريري الكامل للتفاعل بين الدوائين بشكل ديناميكي ومبسط.
    """
    # تهيئة واستبدال الصيغ النصية التلقائية بأسماء الأدوية الفعلية
    text = interaction_text.replace("(.*)", "{}")
    text = text.format(drug1, drug2)

    # البحث عن تفاصيل القاعدة الطبية المطابقة بدلاً من استخدام عشرات جمل if
    matched_rule = find_rule(text)

    return {
        "severity": matched_rule["severity"],
        "interaction": text,
        "mechanism": matched_rule["mechanism"],
        "recommendation": matched_rule["recommendation"],
        "monitoring": matched_rule["monitoring"],
    }
