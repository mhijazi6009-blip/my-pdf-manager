import streamlit as st
import os
import shutil
import base64
import time

# 1. إعدادات الصفحة لتكون الواجهة عريضة ومريحة للمعاينة
st.set_page_config(layout="wide", page_title="مكتبة عروض الأسعار الذكية", page_icon="📁")

# 2. إنشاء المجلد الرئيسي للبيانات إذا لم يكن موجوداً
BASE_DIR = "clients_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

st.title("📁 عروض أسعار العملاء")

# --- القائمة الجانبية (إضافة عميل) ---
with st.sidebar:
    st.header("إضافة عميل جديد")
    new_client = st.text_input("اسم العميل الجديد", placeholder="مثلاً: شركة بلوم باك")
    if st.button("إنشاء المجلد"):
        if new_client:
            path = os.path.join(BASE_DIR, new_client)
            if not os.path.exists(path):
                os.makedirs(path)
                st.success(f"تم إنشاء مجلد: {new_client}")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("هذا العميل موجود بالفعل!")

# 3. جلب قائمة العملاء الحالية
clients = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

if clients:
    # السطر العلوي: اختيار العميل وأزرار الإدارة
    col_select, col_edit, col_delete = st.columns([4, 1, 1])
    
    with col_select:
        selected_client = st.selectbox("اختر العميل للعمل عليه:", clients, label_visibility="collapsed")
        client_path = os.path.join(BASE_DIR, selected_client)

    with col_edit:
        if st.button("✏️ تعديل", help="تغيير اسم العميل"):
            st.session_state.edit_mode = True

    with col_delete:
        if st.button("🗑️ حذف", help="حذف العميل وكل ملفاته نهائياً"):
            st.session_state.delete_mode = True

    # --- منطق حذف العميل (كامل بالمجلد) ---
    if st.session_state.get('delete_mode'):
        st.error(f"‼️ هل أنت متأكد من حذف '{selected_client}' وجميع ملفاته؟")
        c_y, c_n = st.columns(2)
        if c_y.button("نعم، احذف الآن"):
            try:
                # إغلاق أي جلسات متعلقة بالملفات قبل الحذف لتجنب PermissionError
                time.sleep(0.5)
                shutil.rmtree(client_path)
                st.session_state.delete_mode = False
                st.success("تم الحذف بنجاح")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ في الوصول: {e}. تأكد أن المجلد غير مفتوح في برنامج آخر.")
        if c_n.button("إلغاء"):
            st.session_state.delete_mode = False
            st.rerun()

    # --- منطق تعديل اسم العميل ---
    if st.session_state.get('edit_mode'):
        new_name = st.text_input("الاسم الجديد للعميل:", value=selected_client)
        c1, c2 = st.columns(2)
        if c1.button("حفظ التعديل"):
            if new_name and new_name != selected_client:
                os.rename(client_path, os.path.join(BASE_DIR, new_name))
                st.session_state.edit_mode = False
                st.rerun()
        if c2.button("إغلاق التعديل"):
            st.session_state.edit_mode = False
            st.rerun()

    st.divider()

    # 4. رفع الملفات (خاص بكل عميل)
    st.subheader(f"إدارة ملفات: {selected_client}")
    
    # استخدام Key ديناميكي يمنع تداخل الملفات بين العملاء
    uploaded_files = st.file_uploader(
        "اسحب ملفات PDF هنا أو اختر من جهازك", 
        type="pdf", 
        accept_multiple_files=True,
        key=f"uploader_{selected_client}" 
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_dest = os.path.join(client_path, uploaded_file.name)
            if not os.path.exists(file_dest):
                with open(file_dest, "wb") as f:
                    f.write(uploaded_file.getbuffer())
        st.success("تم رفع الملفات بنجاح!")
        time.sleep(0.5)
        st.rerun() # تحديث فوري لعرض الملفات المرفوعة

    # 5. عرض الملفات المرفوعة ومعاينتها
    files = os.listdir(client_path)
    if files:
        st.write(f"إجمالي الملفات: {len(files)}")
        for file in files:
            file_path = os.path.join(client_path, file)
            f_col1, f_col2, f_col3 = st.columns([3, 1, 1])
            
            f_col1.write(f"📄 {file}")
            
            with open(file_path, "rb") as f:
                f_col2.download_button("تحميل", f, file_name=file, key=f"dl_{selected_client}_{file}")
            
            if f_col3.button("حذف الملف", key=f"del_{selected_client}_{file}"):
                os.remove(file_path)
                st.rerun()

            # --- جزء المعاينة المطور لحل مشكلة Chrome ---
            with st.expander(f"👁️ معاينة سريعة لملف: {file}"):
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # استخدام HTML Object لضمان العرض في Chrome وEdge
                pdf_display = f'''
                <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="800px">
                    <embed src="data:application/pdf;base64,{base64_pdf}" type="application/pdf" />
                    <p>متصفحك لا يدعم المعاينة المباشرة. <a href="data:application/pdf;base64,{base64_pdf}" download="{file}">اضغط هنا لتحميل الملف</a>.</p>
                </object>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.info("لا توجد ملفات مرفوعة لهذا العميل حتى الآن.")

else:
    st.info("مرحباً بك! ابدأ بإنشاء أول مجلد عميل من القائمة الجانبية.")
