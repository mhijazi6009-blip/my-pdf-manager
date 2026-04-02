import streamlit as st
import os
import shutil
import base64
import time

# إعدادات الصفحة
st.set_page_config(layout="wide", page_title="عروض الأسعار")

BASE_DIR = "clients_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

st.title("📁 عروض أسعار العملاء")

# القائمة الجانبية
with st.sidebar:
    st.header("إضافة عميل جديد")
    new_client = st.text_input("اسم العميل")
    if st.button("➕ إنشاء مجلد"):
        if new_client:
            path = os.path.join(BASE_DIR, new_client)
            if not os.path.exists(path):
                os.makedirs(path)
                st.success(f"تم إنشاء مجلد لـ {new_client}")
                st.rerun()

# جلب قائمة العملاء
clients = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

if clients:
    col_select, col_edit, col_delete = st.columns([4, 1, 1])
    
    with col_select:
        selected_client = st.selectbox("اختر العميل الحالي:", clients, label_visibility="collapsed")
        client_path = os.path.join(BASE_DIR, selected_client)

    with col_edit:
        if st.button("✏️"):
            st.session_state.edit_mode = True

    with col_delete:
        if st.button("🗑️"):
            st.session_state.delete_mode = True

    # منطق الحذف المعدل لتجنب PermissionError
    if st.session_state.get('delete_mode'):
        st.error(f"هل أنت متأكد من حذف '{selected_client}' نهائياً؟")
        c_y, c_n = st.columns(2)
        if c_y.button("نعم، احذف"):
            try:
                # محاولة إغلاق أي ارتباطات بالملفات قبل الحذف
                st.info("جاري الحذف...")
                time.sleep(0.5) # وقت قصير جداً ليفهم الويندوز أننا أغلقنا المعاينة
                shutil.rmtree(client_path)
                st.session_state.delete_mode = False
                st.success("تم الحذف بنجاح")
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحذف: {e}. جرب إغلاق الملف إذا كان مفتوحاً في برنامج آخر.")
        
        if c_n.button("تراجع"):
            st.session_state.delete_mode = False
            st.rerun()

    # منطق التعديل
    if st.session_state.get('edit_mode'):
        new_name = st.text_input("الاسم الجديد:", value=selected_client)
        if st.button("حفظ الاسم"):
            try:
                os.rename(client_path, os.path.join(BASE_DIR, new_name))
                st.session_state.edit_mode = False
                st.rerun()
            except Exception as e:
                st.error(f"خطأ في تعديل الاسم: {e}")

    st.divider()

    st.subheader(f"العميل المختار: {selected_client}")
    
    # الرفع مع ميزة التحديث الفوري
    uploaded_files = st.file_uploader(
        "ارفع ملفات PDF هنا", 
        type="pdf", 
        accept_multiple_files=True,
        key=f"uploader_{selected_client}"
    )

    if uploaded_files:
        files_saved = False
        for uploaded_file in uploaded_files:
            file_dest = os.path.join(client_path, uploaded_file.name)
            if not os.path.exists(file_dest):
                with open(file_dest, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                files_saved = True
        
        if files_saved:
            st.success("تم رفع الملفات!")
            time.sleep(0.5) # مهلة بسيطة للتأكد من انتظام الكتابة على القرص
            st.rerun() # هذا الأمر سيحدث الصفحة فوراً ويظهر الملفات

    # عرض الملفات
    if os.path.exists(client_path):
        files = os.listdir(client_path)
        if files:
            for file in files:
                file_path = os.path.join(client_path, file)
                f_col1, f_col2, f_col3 = st.columns([3, 1, 1])
                f_col1.write(f"📄 {file}")
                
                with open(file_path, "rb") as f:
                    f_col2.download_button("تحميل", f, file_name=file, key=f"dl_{selected_client}_{file}")
                
                if f_col3.button("حذف", key=f"del_{selected_client}_{file}"):
                    os.remove(file_path)
                    st.rerun()

                with st.expander(f"معاينة {file}"):
                    with open(file_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.info("لا توجد ملفات.")
else:
    st.info("لا يوجد عملاء.")
