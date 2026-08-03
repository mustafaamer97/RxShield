import re
import streamlit as st
from utils.clinical_rules import RULES


def find_rule(text):
    """
    يبحث عن القواعد الطبية المطابقة للنص بناءً على مصفوفة الكلمات المفتاحية (keywords).
    يقوم بفرز النتائج تنازلياً حسب الخطورة ودمج الآليات والتوصيات بدون تكرار.
    """
    lower = text.lower()
    matches = []

    for rule in RULES:
        for keyword in rule["keywords"]:
            if keyword.lower() in lower:
                matches.append(rule)
                break  # تجنب إضافة نفس القاعدة مرتين إذا وجد مرادفين في نفس النص

    if not matches:
        return {
            "severity": "🟢 Minor",
            "mechanism": "Unknown mechanism.",
            "recommendation": "Clinical monitoring.",
            "monitoring": "Routine monitoring.",
        }

    severity_order = {
        "🔴 Critical": 3,
        "🟠 Moderate": 2,
        "🟢 Minor": 1,
    }

    matches.sort(
        key=lambda r: severity_order.get(r["severity"], 0),
        reverse=True,
    )

    return {
        "severity": matches[0]["severity"],
        "mechanism": " | ".join(
            dict.fromkeys(r["mechanism"] for r in matches)
        ),
        "recommendation": " | ".join(
            dict.fromkeys(r["recommendation"] for r in matches)
        ),
        "monitoring": " | ".join(
            dict.fromkeys(r["monitoring"] for r in matches)
        ),
    }


def classify_severity(text):
    """
    ملاحظة: تم الاحتفاظ بهذه الدالة فقط كخيار احتياطي (Fallback) في الملف
    إذا استدعتها ملفات أخرى، لكن الاعتماد الأساسي أصبح الآن على find_rule.
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
    بناء التقرير السريري الكامل للتفاعل بين الدوائين بشكل ديناميكي مبسط
    باستخدام قاموس القواعد الموحد بدون أي جمل شرطية معقدة.
    """
    # 1. صياغة النص وإدراج أسماء الأدوية الحالية مكان علامات الاستبدال (.*)
    text = interaction_text.replace("(.*)", "{}")
    text = text.format(drug1, drug2)

    # 2. استدعاء القاعدة المطابقة ديناميكياً بناءً على الكلمات المفتاحية المتعددة
    rule = find_rule(text)

    # 3. إرجاع القاموس النهائي المهيكل لـ RxShield مباشرة
    return {
        "severity": rule["severity"],
        "interaction": text,
        "mechanism": rule["mechanism"],
        "recommendation": rule["recommendation"],
        "monitoring": rule["monitoring"],
    }


def render_report(report):
    """
    يقوم برسم وعرض عناصر التقرير الطبي السريري بالكامل على واجهة تطبيق Streamlit 
    بناءً على مستوى الخطورة والملاحظات الطبية المرفقة.
    """
    st.markdown("# 🛡️ RxShield Clinical Report")

    st.error(report["severity"])

    st.markdown("## 🧬 Clinical Effect")
    st.info(report["interaction"])

    st.markdown("## 📋 Recommendation")
    st.success(report["recommendation"])

    st.markdown("## ⚙️ Mechanism")
    st.info(report["mechanism"])

    st.markdown("## 🩺 Monitoring")
    st.warning(report["monitoring"])

    st.markdown("## 📚 Evidence")
    st.caption("DrugBank Knowledge Base")

    st.markdown("## ⚠️ Clinical Notes")

    if "Critical" in report["severity"]:
        st.error(
            "This interaction may result in serious patient harm. "
            "Evaluate risk versus benefit before co-administration."
        )

    elif "Moderate" in report["severity"]:
        st.warning(
            "The combination can usually be used with appropriate monitoring."
        )

    else:
        st.success(
            "No major precautions beyond routine monitoring."
        )
