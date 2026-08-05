import json
import os

# قواميس البحث الفوري (Global Dictionaries)
NAME_TO_ID = {}
ID_TO_NAME = {}
DRUGS = {}


def load_drug_info():
    """
    Load drug_info.json from the project root.
    """

    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "drug_info.json",
    )

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print("Drug Info Error:", e)
        return {}


def load_drug_data():
    """تحميل بيانات الأدوية وبناء قواميس البحث السريع"""
    global DRUGS, NAME_TO_ID, ID_TO_NAME

    # استخدام الدالة المضافة للتحميل من المسار الجديد
    DRUGS = load_drug_info()

    if DRUGS:
        # بناء القواميس لتسهيل عملية البحث
        for drug_id, info in DRUGS.items():
            name = info.get("name", "").strip()
            if name:
                NAME_TO_ID[name.lower()] = drug_id
                ID_TO_NAME[drug_id] = name

        print("تم تحميل بيانات الأدوية بنجاح.")
        # طباعة العنصر الأول للتأكد من بنية الملف
        print("عينة من البيانات:", next(iter(DRUGS.items())))


def load_food_interactions():
    """تحميل ملف التفاعلات بين الأدوية والأطعمة"""
    try:
        with open(
            "Drug to Food interactions Dataset.json",
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)
    except FileNotFoundError:
        print(
            "خطأ: لم يتم العثور على ملف Drug to Food interactions Dataset.json"
        )
        return {}


# --- تشغيل الدوال وتحميل البيانات ---
load_drug_data()
food_interactions = load_food_interactions()
