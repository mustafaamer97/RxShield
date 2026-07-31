import sqlite3
import zipfile
from pathlib import Path

# إعداد مسارات الملفات
DB_FILE = Path("all_id_interaction.db")
ZIP_FILE = Path("all_id_interaction.zip")


def get_connection():
    """إنشاء اتصال آمن بقاعدة البيانات SQLite وفك الضغط تلقائياً إذا لزم الأمر."""
    if not DB_FILE.exists():
        with zipfile.ZipFile(ZIP_FILE, "r") as z:
            z.extractall(".")

    conn = sqlite3.connect(DB_FILE)
    # تفعيل Row_factory لتمكين قراءة الأعمدة بالأسماء بدلاً من الفهارس الرقمية
    conn.row_factory = sqlite3.Row

    return conn


def get_interaction(drug1_id, drug2_id):
    """
    البحث التبادلي الذكي عن التداخل بين دوائين باستخدام الـ ID.
    يفحص (الدواء 1 مع 2) أو (الدواء 2 مع 1) لضمان الدقة بغض النظر عن الترتيب.
    """
    conn = get_connection()

    # استعلام SQL محمي ومحسن لجلب أول نتيجة تطابق التداخل الدوائي
    row = conn.execute(
        """
        SELECT *
        FROM interactions
        WHERE 
            ("Drug1 ID" = ? AND "Drug2 ID" = ?)
            OR 
            ("Drug1 ID" = ? AND "Drug2 ID" = ?)
        LIMIT 1;
        """,
        (
            drug1_id,
            drug2_id,
            drug2_id,
            drug1_id
        )
    ).fetchone()

    # إغلاق الاتصال فوراً بعد جلب النتيجة لتحرير الذاكرة
    conn.close()

    return row
