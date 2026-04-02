import streamlit as st
import os
import shutil
import base64
import time

# 1. إعدادات الصفحة (الوضع العريض للمعاينة)
st.set_page_config(layout="wide", page_title="مكتبة عروض الأسعار الذكية", page_icon="📁")

# 2. إنشاء المجلد الرئيسي
BASE_DIR = "clients_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

st.title("📁 نظام إدارة عروض أسعار العملاء")

# --- القائمة الجانبية (إدارة العملاء) ---
with st.sidebar:
    st.header("إضافة عميل جديد")
    new_client = st.text_input("اسم العميل الجديد", placeholder="مثلاً: شركة بلوم باك")
    if st.button("➕ إنشاء المجلد"):
        if new_client:
            path = os.path.join(BASE_DIR, new_client)
            if not os.path.exists(path):
                os.makedirs(path)
                st.success(f"تم إنشاء مجلد: {new_client}")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("هذا العميل موجود بالفعل!")

# 3. جلب قائمة العملاء
clients = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]

if clients:
    # تنسيق الجزء العلوي (الاختيار، التعديل، الحذف)
    col_select, col_edit, col_delete = st.columns([4, 1, 1])
    
    with col_select:
        selected_client = st.selectbox("اختر العميل:", clients, label_visibility="collapsed")
        client_path = os.path.join(BASE_DIR, selected_client)

    with col_edit:
        if st.button("✏️ تعديل"):
            st.session_state.edit_mode = True

    with col_delete:
        if st.button("🗑️ حذف"):
            st.session_state.delete_mode = True

    # --- منطق الحذف الكامل ---
    if st.session_state.get('delete_mode'):
        st.error(f"⚠️ هل أنت متأكد من حذف العميل '{selected_client}' وكل محتوياته؟")
        c_y, c_n = st.columns(2)
        if c_y.button("نعم، احذف نهائياً"):
            try:
                time.sleep(0.5)
                shutil.rmtree(client_path)
                st.session_state.delete_mode = False
                st.rerun()
            except Exception as e:
                st.error(f"فشل الحذف: {e}")
        if c_n.button("إلغاء الحذف"):
            st.session_state.delete_mode = False
            st.rerun()

    # --- منطق تعديل الاسم ---
    if st.session_state.get('edit_mode'):
        new_name = st.text_input("الاسم الجديد:", value=selected_client)
        if st.button("تحديث الاسم الآن"):
            if new_name and new_name != selected_client:
                os.rename(client_path, os.path.join(BASE_DIR, new_name))
                st.session_state.edit_mode = False
                st.rerun()

    st.divider()

    # 4. رفع الملفات
    st.subheader(f"📂 ملفات العميل: {selected_client}")
    uploaded_files = st.file_uploader(
        "ارفع ملفات PDF", 
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
        st.success("تم الرفع!")
        time.sleep(0.5)
        st.rerun()

    # 5. عرض الملفات والمعاينة المتقدمة
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

            # --- جزء المعاينة الذكي المحسن ---
            with st.expander(f"👁️ معاينة {file}"):
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                
                # استخدام رابط معاينة متوافق أكثر مع Chrome
                pdf_url = f"data:application/pdf;base64,{base64_pdf}"
                
                # المعاينة داخل إطار
                st.markdown(
                    f'<iframe src="{pdf_url}" width="100%" height="800px" style="border:none;"></iframe>', 
                    unsafe_allow_html=True
                )
                
                # رابط احتياطي يفتح في صفحة جديدة (يحل مشكلة الحظر تماماً)
                st.markdown(
                    f'<div style="text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 5px;">'
                    f'إذا لم تظهر المعاينة أعلاه، <a href="{pdf_url}" target="_blank" style="color: #ff4b4b; font-weight: bold; text-decoration: none;">اضغط هنا لفتح الملف في نافذة مستقلة 🚀</a>'
                    f'</div>', 
                    unsafe_allow_html=True
                )
    else:
        st.info("المجلد فارغ.")

else:
    st.info("ابدأ بإنشاء عميل من القائمة الجانبية.")
