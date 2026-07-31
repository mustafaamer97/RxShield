import streamlit as st
from database.db import get_connection

st.set_page_config(page_title="RxShield")

st.title("🛡️ RxShield")

try:
    # 1. إنشاء الاتصال بقاعدة البيانات
    conn = get_connection()
    st.success("Database Connected ✅")

    # 2. جلب اسم أول جدول متوفر
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchone()

    if table:
        try:
            table_name = table["name"]
        except (TypeError, IndexError):
            table_name = table[0]

        st.write("Table:", table_name)

        # 3. حساب العدد الإجمالي للسجلات
        count = conn.execute(
            f"SELECT COUNT(*) FROM `{table_name}`;"
        ).fetchone()[0]

        st.write("Total Records:", f"{count:,}")
        
        st.markdown("---") # خط فاصل لتنظيم الواجهة

        # 4. جلب وعرض أول 5 تفاعلات دوائية (التعديل الجديد)
        rows = conn.execute(
            f"SELECT * FROM `{table_name}` LIMIT 5;"
        ).fetchall()

        st.subheader("First 5 Drug Interactions")

        for row in rows:
            try:
                # محاولة تحويل الصف إلى قاموس مباشرة (تنجح إذا تم ضبط row_factory)
                st.write(dict(row))
            except (TypeError, ValueError):
                # خطة بديلة إذا لم يكن row_factory مفعلًا كـ sqlite3.Row
                st.write(list(row))
                
    else:
        st.warning("⚠️ Connected, but no tables found in the database.")

    # 5. إغلاق الاتصال بأمان
    conn.close()

except Exception as e:
    st.error(str(e))
