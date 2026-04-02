import streamlit as st
import os
import shutil

# إعدادات الصفحة (لتكون المعاينة كبيرة)
st.set_page_config(layout="wide", page_title="مكتبة عروض الأسعار")

# المجلد الرئيسي الذي سيحتوي على بيانات العملاء
BASE_DIR = "clients_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

st.title("📁 نظام إدارة عروض أسعار العملاء")

# القائمة الجانبية لإدارة العملاء
with st.sidebar:
    st.header("إدارة العملاء")
    new_client = st.text_input("اسم عميل جديد:")
    if st.button("إنشاء فولدر"):
        if new_client:
            path = os.path.join(BASE_DIR, new_client)
            if not os.path.exists(path):
                os.makedirs(path)
                st.success(f"تم إنشاء مجلد لـ {new_client}")
            else:
                st.warning("العميل موجود بالفعل")

# الحصول على قائمة العملاء (المجلدات)
clients = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

if clients:
    selected_client = st.selectbox("اختر العميل:", clients)
    client_path = os.path.join(BASE_DIR, selected_client)

    # صفوف للعمليات الأساسية (تعديل وحذف المجلد)
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("تعديل اسم العميل:", value=selected_client)
        if st.button("تحديث الاسم"):
            os.rename(client_path, os.path.join(BASE_DIR, new_name))
            st.rerun()
    
    with col2:
        if st.button("❌ حذف العميل بكل ملفاته"):
            shutil.rmtree(client_path)
            st.rerun()

    st.divider()

    # رفع ملفات PDF
    uploaded_files = st.file_uploader("ارفع ملفات PDF للعميل", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with open(os.path.join(client_path, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("تم رفع الملفات بنجاح!")

    # عرض الملفات المرفوعة
    st.subheader(f"ملفات العميل: {selected_client}")
    files = os.listdir(client_path)
    
    if files:
        for file in files:
            file_path = os.path.join(client_path, file)
            col_f1, col_f2, col_f3 = st.columns([3, 1, 1])
            
            with col_f1:
                st.write(f"📄 {file}")
            
            with col_f2:
                # زر التحميل
                with open(file_path, "rb") as f:
                    st.download_button("تحميل", f, file_name=file)
            
            with col_f3:
                # زر الحذف
                if st.button("حذف", key=file):
                    os.remove(file_path)
                    st.rerun()

            # ميزة المعاينة (العرض)
            with st.expander(f"معاينة ملف: {file}"):
                with open(file_path, "rb") as f:
                    base64_pdf = f.read()
                    # كود لعرض الـ PDF داخل المتصفح بمساحة كبيرة
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf.hex()}" width="100%" height="600" type="application/pdf"></iframe>'
                    # ملاحظة: التحويل لـ hex هو طريقة بسيطة، للأفضل نستخدم base64 (سنعدلها لاحقاً لو واجهت مشكلة)
                    st.markdown(f'<iframe src="data:application/pdf;base64,{__import__("base64").b64encode(base64_pdf).decode("utf-8")}" width="100%" height="800" type="application/pdf"></iframe>', unsafe_allow_html=True)
    else:
        st.info("لا توجد ملفات لهذا العميل بعد.")
else:
    st.info("ابدأ بإنشاء أول عميل من القائمة الجانبية.")