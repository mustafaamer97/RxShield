# utils/clinical_engine.py

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
            "interpretation": "Clinical significance requires professional assessment.",
            "interaction_type": "Unknown"
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

    # جمع الحقول الفرعية مع دعم المفاتيح الجديدة المضافة في القواعد
    return {
        "severity": matches[0]["severity"],
        "mechanism": " | ".join(
            dict.fromkeys(r["mechanism"] for r in matches if "mechanism" in r)
        ),
        "recommendation": " | ".join(
            dict.fromkeys(r["recommendation"] for r in matches if "recommendation" in r)
        ),
        "monitoring": " | ".join(
            dict.fromkeys(r["monitoring"] for r in matches if "monitoring" in r)
        ),
        "interpretation": matches[0].get(
            "interpretation", 
            "Clinical significance requires professional assessment."
        ),
        "interaction_type": matches[0].get(
            "interaction_type", 
            "Unknown"
        )
    }


def extract_clinical_features(text):
    """
    تستخرج تفاصيل الحركية الدوائية (PK) والديناميكية الدوائية (PD) والإنزيمات 
    المتأثرة (CYP Enzymes) مباشرة من نص التداخل.
    """
    lower = text.lower()

    features = {
        "effect": None,
        "pk_pd": None,
        "enzyme": None,
        "change": None,
    }

    # --------------------------
    # Pharmacokinetics
    # --------------------------
    if "serum concentration" in lower:
        features["pk_pd"] = "Pharmacokinetic"

        if "increase" in lower or "increased" in lower:
            features["effect"] = "Increased serum concentration"
            features["change"] = "Increase"
        elif "decrease" in lower or "decreased" in lower:
            features["effect"] = "Decreased serum concentration"
            features["change"] = "Decrease"

    # --------------------------
    # Therapeutic efficacy
    # --------------------------
    elif "therapeutic efficacy" in lower:
        features["pk_pd"] = "Pharmacodynamic"
        features["effect"] = "Reduced therapeutic efficacy"

    # --------------------------
    # Bleeding
    # --------------------------
    elif "bleeding" in lower or "hemorrhage" in lower:
        features["pk_pd"] = "Pharmacodynamic"
        features["effect"] = "Major bleeding risk"

    # --------------------------
    # QT
    # --------------------------
    elif "qtc prolongation" in lower:
        features["pk_pd"] = "Pharmacodynamic"
        features["effect"] = "QT prolongation"

    # --------------------------
    # Arrhythmia
    # --------------------------
    elif "arrhythmia" in lower:
        features["pk_pd"] = "Pharmacodynamic"
        features["effect"] = "Cardiac arrhythmia"

    # --------------------------
    # CYP Enzymes
    # --------------------------
    if "cyp3a4" in lower:
        features["enzyme"] = "CYP3A4"
    elif "cyp2d6" in lower:
        features["enzyme"] = "CYP2D6"
    elif "cyp2c9" in lower:
        features["enzyme"] = "CYP2C9"
    elif "cyp2c19" in lower:
        features["enzyme"] = "CYP2C19"

    return features


def enhance_recommendation(report):
    """
    تقوم بتعديل التوصيات ديناميكياً لتوفير إرشادات سريرية دقيقة وقابلة للتطبيق 
    بناءً على الكلمات المفتاحية الحرجة الموجودة في نص التداخل.
    """
    text = report["interaction"].lower()

    # Bleeding
    if "bleeding" in text or "hemorrhage" in text:
        report["recommendation"] = (
            "Avoid combination whenever possible. "
            "If unavoidable, monitor INR closely and educate the patient about bleeding symptoms."
        )

    # QT
    elif "qtc prolongation" in text:
        report["recommendation"] = (
            "Avoid combining multiple QT-prolonging drugs. "
            "Correct electrolyte abnormalities and obtain baseline ECG."
        )

    # CYP3A4
    elif "cyp3a4" in text:
        report["recommendation"] = (
            "Dose adjustment may be required because of CYP3A4 interaction."
        )

    # Serum concentration
    elif "serum concentration" in text:
        report["recommendation"] = (
            "Consider therapeutic drug monitoring and dose adjustment."
        )

    return report


def build_report(interaction_text, drug1, drug2):
    """
    بناء التقرير السريري الكامل للتفاعل بين الدوائين بشكل ديناميكي مبسط
    مع ربط السمات السريرية وتعزيز التوصيات الطبية مباشرة.
    """
    # 1. صياغة النص وإدراج أسماء الأدوية الحالية مكان علامات الاستبدال (.*)
    text = interaction_text.replace("(.*)", "{}")
    text = text.format(drug1, drug2)

    # 2. استدعاء القاعدة المطابقة ديناميكياً بناءً على الكلمات المفتاحية
    rule = find_rule(text)

    # 3. استخراج المظهر والنوع والإنزيمات سريرياً (احتياطي للبيانات القديمة)
    features = extract_clinical_features(text)

    # 4. صياغة القاموس الأولي للتقرير بناءً على التعديل الجديد المطلوب
    report = {
        "severity": rule["severity"],
        "interaction": text,
        "interpretation": rule.get(
            "interpretation",
            "Clinical significance requires professional assessment."
        ),
        "interaction_type": rule.get(
            "interaction_type",
            features["pk_pd"] if features["pk_pd"] else "Unknown"
        ),
        "enzyme": features["enzyme"],
        "mechanism": rule["mechanism"],
        "recommendation": rule["recommendation"],
        "monitoring": rule["monitoring"],
    }

    # 5. تعزيز وتخصيص التوصية الطبية قبل الإرجاع
    report = enhance_recommendation(report)

    return report


def render_report(report):
    """
    يقوم برسم وعرض عناصر التقرير الطبي السريري بالكامل على واجهة تطبيق Streamlit 
    بناءً على مستوى الخطورة والملاحظات الطبية المرفقة.
    """
    st.markdown("# 🛡️ RxShield Clinical Report")

    st.error(report["severity"])

    st.markdown("## 🧬 Clinical Effect")
    st.info(report["interaction"])

    # التعديل الجديد: إدراج حقول الـ Interpretation و Interaction Type مباشرة بعد الـ Clinical Effect
    st.markdown("## Clinical Interpretation")
    st.success(report["interpretation"])

    st.markdown("## 🧪 Interaction Type")
    st.success(report["interaction_type"])

    if report["enzyme"]:
        st.markdown("## 🧬 Enzyme")
        st.info(report["enzyme"])

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
