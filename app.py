import streamlit as st
import zipfile
import os

st.title("🛡️ RxShield: Testing Zip Contents")

# التحقق من وجود الملف المضغوط
zip_filename = "all_id_interaction.zip"

if os.path.exists(zip_filename):
    st.success(f"✅ تم العثور على الملف {zip_filename} في السيرفر!")
    
    # فحص محتويات الملف المضغوط وطباعتها
    with zipfile.ZipFile(zip_filename, "r") as z:
        file_list = z.namelist()
        st.write("🔍 المحتويات المكتشفة داخل ملف الـ ZIP هي:")
        st.code(file_list)
else:
    st.error(f"❌ لم يتم العثور على الملف {zip_filename}. تأكد من وجوده في نفس المجلد الرئيسي على GitHub.")
