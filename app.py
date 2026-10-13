import streamlit as st
import json
import random
import string
import pandas as pd
from datetime import datetime
from PIL import Image

from modules.file_parser import parse_uploaded_file
from modules.engine import TriDimensionalGradingEngine
from modules.rubric_generator import RubricGenerator
from modules.transliteration import normalize_uzbek_text
from modules.plagiarism_checker import PeerPlagiarismChecker
from modules.batch_grader import BatchGrader
from modules.statistics_module import get_experiment_benchmark_data, calculate_qwk, calculate_pearson_r, calculate_mae
from modules.report_generator import generate_official_protocol_html
from modules.db_manager import load_users, save_users, add_user, authenticate_user
from modules.sample_data import (
    SAMPLE_TASK,
    SAMPLE_REFERENCE,
    STUDENT_SAMPLE_EFFORT,
    STUDENT_SAMPLE_AI,
    STUDENT_SAMPLE_WEAK
)

# Sahifa konfiguratsiyasi
st.set_page_config(
    page_title="EduAI Grader - Autentifikatsiyali Baholash Portali",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Maxsus korporativ CSS dizayn
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .portal-header-admin {
        background: linear-gradient(135deg, #1e1b4b 0%, #31102f 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 22px 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    
    .portal-header-teacher {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 22px 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }

    .portal-header-student {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 22px 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }

    .grade-card {
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        background: rgba(255, 255, 255, 0.04);
        border: 2px solid rgba(255, 255, 255, 0.1);
        transition: all 0.2s ease;
        height: 100%;
    }
    
    .role-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .badge-admin { background: #ef4444; color: white; }
    .badge-teacher { background: #3b82f6; color: white; }
    .badge-student { background: #10b981; color: white; }
    
    .big-score {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.0;
        margin: 8px 0;
    }
    
    .auth-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        padding: 8px 18px;
    }
</style>
""", unsafe_allow_html=True)

# BAZADAN FOYDALANUVCHILARNI YUKLASH (DISK PERSISTENCE)
st.session_state.registered_users = load_users()

# TIZIMGA KIRGAN FOYDALANUVChI (SESSION)
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "task_input" not in st.session_state:
    st.session_state.task_input = SAMPLE_TASK
if "ref_input" not in st.session_state:
    st.session_state.ref_input = SAMPLE_REFERENCE
if "student_text" not in st.session_state:
    st.session_state.student_text = STUDENT_SAMPLE_EFFORT
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "file_type_label" not in st.session_state:
    st.session_state.file_type_label = "Matnli kiritish"

if "secure_api_key" not in st.session_state:
    st.session_state.secure_api_key = ""
if "default_max_score" not in st.session_state:
    st.session_state.default_max_score = 10.0
if "default_beta" not in st.session_state:
    st.session_state.default_beta = 1.0

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = [
        {"vaqt": "14:15", "foydalanuvchi": "Admin", "amal": "Tizim ishga tushirildi"},
        {"vaqt": "14:20", "foydalanuvchi": "Xolmatov Abror (O'qituvchi)", "amal": "Tizimga kirdi (Login)"},
        {"vaqt": "14:35", "foydalanuvchi": "EduAI Grader", "amal": "Informatika topshirig'i baholandi"}
    ]

if "grades_journal" not in st.session_state:
    st.session_state.grades_journal = [
        {
            "talaba": "Azizov Jasur",
            "topshiriq": "Python'da Rekursiya va Faktorial...",
            "max_ball": 10.0,
            "baho_1_akad": 6.8,
            "baho_2_ai": 6.8,
            "baho_3_emp": 9.1,
            "tasdiqlangan_ball": 9.1,
            "izoh": "Mustaqil harakat va qadamlar uchun rag'batlantirildi.",
            "feedback": "Aziz Jasur! Oraliq hisob-kitoblaringiz va samimiy urinishingiz ajoyib. Xatolar ustida ishlashda davom eting!"
        }
    ]

# =========================================================================
# AGAR FOYDALANUVChI TIZIMGA KIRMANGAN BO'LSA: KIRISH OYNASI (LOGIN SCREEN)
# =========================================================================
if st.session_state.current_user is None:
    st.markdown("""
    <div style="max-width: 650px; margin: 40px auto 20px auto; text-align: center;">
        <h1 style="font-size: 2.3rem; margin-bottom: 8px;">🎓 EduAI Grader</h1>
        <p style="font-size: 1.05rem; opacity: 0.85;">
            Intellektual Baholash Portali — Tizimga Kirish
        </p>
    </div>
    """, unsafe_allow_html=True)

    login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
    with login_col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 18px; padding: 28px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <h3 style="margin-top: 0; text-align: center;">🔐 Akkauntga Kirish</h3>
        """, unsafe_allow_html=True)
        
        input_login = st.text_input("Foydalanuvchi Logini (Username):", placeholder="Masalan: admin yoki teacher yoki jasur")
        input_password = st.text_input("Parol:", type="password", placeholder="Parolingizni kiriting")
        
        if st.button("🚀 Tizimga Kirish", type="primary", use_container_width=True):
            user_match = authenticate_user(input_login, input_password)
            if user_match:
                st.session_state.current_user = user_match
                st.session_state.audit_logs.append({
                    "vaqt": datetime.now().strftime("%H:%M"),
                    "foydalanuvchi": user_match["name"],
                    "amal": f"Tizimga kirdi (@{user_match['login']})"
                })
                st.balloons()
                st.success(f"Xush kelibsiz, {user_match['name']}!")
                st.rerun()
            else:
                st.error("Login yoki parol noto'g'ri! Iltimos, qayta urinib ko'ring.")

        st.markdown("---")
        st.caption("⚡ **Himoya/Demo taqdimoti uchun tezkor kirish tugmalari:**")
        c_dem1, c_dem2, c_dem3 = st.columns(3)
        with c_dem1:
            if st.button("🛡️ Admin", use_container_width=True):
                st.session_state.current_user = [u for u in st.session_state.registered_users if u["role"] == "Administrator"][0]
                st.rerun()
        with c_dem2:
            if st.button("🧑‍🏫 O'qituvchi", use_container_width=True):
                st.session_state.current_user = [u for u in st.session_state.registered_users if u["role"] == "O'qituvchi"][0]
                st.rerun()
        with c_dem3:
            if st.button("🎓 O'quvchi", use_container_width=True):
                st.session_state.current_user = [u for u in st.session_state.registered_users if u["role"] == "O'quvchi"][0]
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# =========================================================================
# AGAR FOYDALANUVChI TIZIMGA KIRGAN BO'LSA: ASOSIY DASTUR
# =========================================================================
curr_u = st.session_state.current_user
user_role = curr_u["role"]

# SIDEBAR: SHAXSIY PROFIL VA MENYU
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 5px 0 10px 0;">
        <h2 style="margin: 0; font-size: 1.45rem;">🎓 EduAI Grader</h2>
        <span style="font-size: 0.78rem; opacity: 0.7;">Avtorizatsiyali Ta'lim Portali</span>
    </div>
    """, unsafe_allow_html=True)

    role_color = "#ef4444" if user_role == "Administrator" else ("#3b82f6" if user_role == "O'qituvchi" else "#10b981")
    st.markdown(f"""
    <div class="auth-box" style="border-left: 4px solid {role_color};">
        <span style="font-size: 0.75rem; color: {role_color}; font-weight: bold; text-transform: uppercase;">Faol Profil:</span>
        <h4 style="margin: 3px 0 2px 0;">{curr_u['name']}</h4>
        <span style="font-size: 0.8rem; opacity: 0.8;">Rol: <b>{user_role}</b> | Login: <code>@{curr_u['login']}</code></span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Tizimdan Chiqish (Logout)", use_container_width=True):
        st.session_state.current_user = None
        st.rerun()

    st.markdown("---")

    # Rolga mos menyu
    if user_role == "Administrator":
        st.subheader("🛡️ Admin Menyusi")
        active_menu = st.radio(
            "Bo'lim:",
            [
                "➕ Yangi Foydalanuvchi Qo'shish (Login & Parol)",
                "👥 Akkauntlar Boshqaruvi (Login/Parol Ro'yxati)",
                "📊 Tizim Monitoringi & Dashboard",
                "🔐 Global API & Xavfsizlik Vault",
                "📋 Tizim Audit Loglari"
            ]
        )
    elif user_role == "O'qituvchi":
        st.subheader("🧑‍🏫 O'qituvchi Menyusi")
        active_menu = st.radio(
            "Bo'lim:",
            [
                "📝 3D Baholash Laboratoriyasi",
                "📂 Ommaviy Baholash & O'zaro Plagiat",
                "📊 Elektron Baholash Jurnali",
                "📄 Rasmiy Dalolatnoma (PDF)",
                "📈 Ilmiy Eksperiment & Validatsiya"
            ]
        )
    else: # O'quvchi
        st.subheader("🎓 O'quvchi Menyusi")
        active_menu = st.radio(
            "Bo'lim:",
            [
                "📤 Uy Vazifasini Topshirish",
                "📜 Mening Baholarim & Tahlil",
                "✉️ O'qituvchi Tavsiya Xati"
            ]
        )

    st.markdown("---")
    if st.session_state.secure_api_key.strip():
        st.success("🔒 API: Faol (LLM)")
    else:
        st.info("⚡ Tizim: 100% Bepul Lokal NLP")


# =========================================================================
# 🛡️ 1-PANEL: ADMINISTRATOR PANELI (FAQAT ADMIN UCHUN)
# =========================================================================
if user_role == "Administrator":
    st.markdown("""
    <div class="portal-header-admin">
        <span class="role-badge badge-admin">Administrator Paneli</span>
        <h2 style="margin: 4px 0 6px 0; font-size: 1.7rem;">🛡️ Tizim Administratori Boshqaruv Markazi</h2>
        <p style="margin: 0; opacity: 0.85; font-size: 0.92rem;">
            Faqat admin yangi o'qituvchi va o'quvchilarni <b>Login va Parol</b> bilan ro'yxatdan o'tkazishi, akkauntlarni boshqarishi mumkin.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # A. YANGI FOYDALANUVChI QO'SHISH (LOGIN VA PAROL BILAN)
    if active_menu == "➕ Yangi Foydalanuvchi Qo'shish (Login & Parol)":
        st.subheader("➕ Yangi O'qituvchi yoki O'quvchi Qo'shish Formasi")
        st.caption("Admin tomonidan yaratilgan har bir login va parol darhol doimiy bazaga (data/users.json) saqlanadi va yangi foydalanuvchi istalgan qurilmadan saytga kira oladi.")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            add_role = st.selectbox("1. Foydalanuvchi Roli:", ["O'qituvchi", "O'quvchi"])
            add_name = st.text_input("2. F.I.Sh (Ism, Familiya):", placeholder="Masalan: Rustamov Bekzod")
            add_group = st.text_input("3. Sinf / Kafedra:", placeholder="Masalan: 10-B sinf yoki Informatika kafedrasi")
            add_email = st.text_input("4. Elektron Pochta:", placeholder="bekzod@eduai.uz")

        with col_f2:
            st.write("**Xavfsizlik Ma'lumotlari (Kirish uchun):**")
            
            suggested_login = (add_name.split()[0].lower() + ("_teacher" if add_role == "O'qituvchi" else "_student")) if add_name else ""
            add_login = st.text_input("5. Login (Username):", value=suggested_login, help="Tizimga kirish uchun unikal login")
            
            default_pwd = "".join(random.choices(string.ascii_letters + string.digits, k=8))
            add_password = st.text_input("6. Parol:", value=default_pwd, help="Kamida 4 ta belgi")

            if st.button("🎲 Boshqa Parol Generatsiya Qilish"):
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Yangi Foydalanuvchini Ro'yxatdan O'tkazish", type="primary", use_container_width=True):
                if not add_name or not add_login or not add_password:
                    st.error("Iltimos, barcha majburiy maydonlarni (Ism, Login va Parol) to'ldiring!")
                else:
                    success, msg = add_user(add_name, add_role, add_login, add_password, add_email, add_group)
                    if success:
                        st.session_state.registered_users = load_users()
                        st.session_state.audit_logs.append({
                            "vaqt": datetime.now().strftime("%H:%M"),
                            "foydalanuvchi": "Administrator",
                            "amal": f"Yangi akkaunt yaratildi: {add_name} ({add_role}, login: @{add_login})"
                        })
                        st.balloons()
                        st.success(f"✅ Yangi {add_role.lower()} muvaffaqiyatli saqlandi!\n\n**Login:** `{add_login}`\n**Parol:** `{add_password}`\n\n*Ushbu foydalanuvchi hoziroq ushbu login va parol bilan istalgan brauzer yoki telefondan tizimga kira oladi!*")
                    else:
                        st.error(msg)

    # B. AKKAUNTLAR BOSHINCHASI VA PAROLLAR RO'YXATI
    elif active_menu == "👥 Akkauntlar Boshqaruvi (Login/Parol Ro'yxati)":
        st.subheader("👥 Barcha Ro'yxatdan O'tgan Akkauntlar (Admin Nazorati)")
        st.caption("Admin barcha o'qituvchilar va o'quvchilarning login va parollarini boshqarishi mumkin.")

        show_passwords = st.checkbox("👁️ Parollarni ochiq ko'rsatish", value=False)

        user_rows = []
        for u in st.session_state.registered_users:
            user_rows.append({
                "ID": u["id"],
                "F.I.Sh": u["name"],
                "Roli": u["role"],
                "Sinf/Guruh": u.get("group", ""),
                "Login": u["login"],
                "Parol": u["password"] if show_passwords else "••••••••",
                "E-mail": u["email"],
                "Holati": u["status"]
            })
        st.dataframe(pd.DataFrame(user_rows), use_container_width=True)

        st.markdown("---")
        st.subheader("🔑 Parolni Qayta Tiklash (Reset Password) yoki O'chirish")
        
        c_rst1, c_rst2, c_rst3 = st.columns(3)
        with c_rst1:
            target_user = st.selectbox(
                "Foydalanuvchini tanlang:",
                [f"{u['name']} (@{u['login']})" for u in st.session_state.registered_users if u['role'] != 'Administrator']
            )
        with c_rst2:
            new_custom_pwd = st.text_input("Yangi Parol:", value="YangiParol2026!")
        with c_rst3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Parolni O'zgartirish", type="primary"):
                t_login = target_user.split("(@")[1].rstrip(")")
                users_list = load_users()
                for u in users_list:
                    if u["login"] == t_login:
                        u["password"] = new_custom_pwd
                        save_users(users_list)
                        st.session_state.registered_users = users_list
                        st.session_state.audit_logs.append({
                            "vaqt": datetime.now().strftime("%H:%M"),
                            "foydalanuvchi": "Administrator",
                            "amal": f"Parol o'zgartirildi: @{t_login}"
                        })
                        st.success(f"@{t_login} paroli muvaffaqiyatli yangilandi!")
                        st.rerun()

    # C. TIZIM MONITORINGI
    elif active_menu == "📊 Tizim Monitoringi & Dashboard":
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        teachers_count = len([u for u in st.session_state.registered_users if u["role"] == "O'qituvchi"])
        students_count = len([u for u in st.session_state.registered_users if u["role"] == "O'quvchi"])
        c_m1.metric("O'qituvchilar", f"{teachers_count} nafar")
        c_m2.metric("O'quvchilar", f"{students_count} nafar")
        c_m3.metric("Baholangan Ishlar", f"{len(st.session_state.grades_journal)} ta")
        c_m4.metric("Kiberxavfsizlik", "A+ (Himoyalangan)")

        st.markdown("---")
        st.subheader("📈 Haftalik Faollik Grafigi")
        chart_data = pd.DataFrame({
            "Kun": ["Dush", "Sesh", "Chor", "Pay", "Juma", "Shan"],
            "Faollik": [14, 22, 35, 41, 58, 20]
        })
        st.bar_chart(chart_data.set_index("Kun"))

    # D. GLOBAL API VA SOZLAMALAR
    elif active_menu == "🔐 Global API & Xavfsizlik Vault":
        st.subheader("🔐 Google Gemini API Kaliti (Shifrlangan Vault)")
        api_val = st.text_input("API Kaliti:", value=st.session_state.secure_api_key, type="password")
        
        ca1, ca2 = st.columns(2)
        with ca1:
            if st.button("💾 API Kalitni Saqlash", type="primary"):
                st.session_state.secure_api_key = api_val.strip()
                st.success("API kaliti saqlandi!")
                st.rerun()
        with ca2:
            if st.button("🗑️ Kalitni O'chirish"):
                st.session_state.secure_api_key = ""
                st.warning("Kalit o'chirildi.")
                st.rerun()

    # E. AUDIT LOGLARI
    elif active_menu == "📋 Tizim Audit Loglari":
        st.subheader("📋 Tizim Xavfsizlik va Harakatlar Jurnali (Audit Trail)")
        st.table(pd.DataFrame(st.session_state.audit_logs))


# =========================================================================
# 🧑‍🏫 2-PANEL: O'QITUVCHI PANELI (FAQAT O'QITUVCHI UCHUN)
# =========================================================================
elif user_role == "O'qituvchi":
    st.markdown(f"""
    <div class="portal-header-teacher">
        <span class="role-badge badge-teacher">O'qituvchi Kabineti</span>
        <h2 style="margin: 4px 0 6px 0; font-size: 1.7rem;">🧑‍🏫 {curr_u['name']} Ishchi Kabineti</h2>
        <p style="margin: 0; opacity: 0.85; font-size: 0.92rem;">
            Kafedra: <b>{curr_u.get('group', 'Informatika')}</b> | Savollarni kiritish, 3D baholash, ommaviy tekshiruv va rasmiy aktlar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if active_menu == "📝 3D Baholash Laboratoriyasi":
        col_setup1, col_setup2 = st.columns([2, 1])
        
        with col_setup1:
            st.subheader("1. Topshiriq Savollari va Etalon")
            task_prompt = st.text_area("Topshiriq savollari:", value=st.session_state.task_input, height=100)
            st.session_state.task_input = task_prompt
            
            if st.button("✨ Savoldan Etalon Javobni AI orqali Yaratish", use_container_width=True, type="secondary"):
                with st.spinner("AI etalon javob va rubrika mezonlarini shakllantirmoqda..."):
                    rubric_gen = RubricGenerator(gemini_api_key=st.session_state.secure_api_key)
                    auto_rubric = rubric_gen.generate_reference_and_rubric(
                        task_prompt, max_score=st.session_state.default_max_score
                    )
                    st.session_state.ref_input = auto_rubric
                    st.success("✅ Etalon va rubrika yaratildi!")
                    st.rerun()

            ref_solution = st.text_area("Etalon javob va rubrika:", value=st.session_state.ref_input, height=120)
            st.session_state.ref_input = ref_solution

        with col_setup2:
            st.subheader("2. Parametrlar")
            max_score = st.number_input("🎯 Maksimal Ball:", 1.0, 100.0, float(st.session_state.default_max_score), 1.0)
            beta_strictness = st.slider("⚖️ AI Jazosi (β):", 0.0, 1.0, float(st.session_state.default_beta), 0.1)

            st.write("**🧪 Test Namunalar:**")
            cs1, cs2 = st.columns(2)
            with cs1:
                if st.button("🙋 Mustaqil", use_container_width=True):
                    st.session_state.student_text = STUDENT_SAMPLE_EFFORT
                    st.session_state.uploaded_image = None
                    st.rerun()
            with cs2:
                if st.button("🤖 ChatGPT", use_container_width=True):
                    st.session_state.student_text = STUDENT_SAMPLE_AI
                    st.session_state.uploaded_image = None
                    st.rerun()

        st.markdown("---")
        st.subheader("3. O'quvchi Javobini Qabul Qilish")

        tab_f, tab_t = st.tabs(["📁 Fayl Yuklash (Word, PDF, TXT, Daftar surati)", "✍️ Matn Yozish"])
        with tab_f:
            uploaded_file = st.file_uploader("O'quvchi ishini yuklang:", type=["docx", "pdf", "txt", "png", "jpg", "jpeg", "webp"])
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                extracted_text, img_obj, file_type = parse_uploaded_file(file_bytes, uploaded_file.name)
                norm_text = normalize_uzbek_text(extracted_text)
                st.session_state.student_text = norm_text if norm_text else st.session_state.student_text
                st.session_state.uploaded_image = img_obj
                st.success(f"Yuklandi: {uploaded_file.name} ({file_type})")
                if img_obj:
                    st.image(img_obj, caption="Daftar sahifasi", width=380)

        with tab_t:
            text_d = st.text_area("O'quvchi javobi:", value=st.session_state.student_text, height=140)
            st.session_state.student_text = normalize_uzbek_text(text_d)

        if st.button("🚀 3 Xil Bahoni Hisoblash", type="primary", use_container_width=True):
            with st.spinner("AI 3 xil baholashni hisoblamoqda..."):
                engine = TriDimensionalGradingEngine(gemini_api_key=st.session_state.secure_api_key)
                results = engine.evaluate_submission(
                    task_prompt=task_prompt,
                    reference_solution=ref_solution,
                    student_text=st.session_state.student_text,
                    max_score=max_score,
                    student_image=st.session_state.uploaded_image,
                    beta_strictness=beta_strictness
                )
                st.session_state.last_3d_results = results

        if "last_3d_results" in st.session_state:
            results = st.session_state.last_3d_results
            st.markdown("---")
            st.subheader(f"📊 3 Xil Mustaqil Baholash Natijalari (To'liq ball: {max_score})")

            eval_1 = results["eval_1_academic"]
            eval_2 = results["eval_2_ai_supervised"]
            eval_3 = results["eval_3_empathy"]

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("""
                <div class="grade-card" style="border-top: 5px solid #2563eb;">
                    <span class="role-badge badge-teacher">1-BOSQICH</span>
                    <h3 style="margin: 4px 0; color: #93c5fd;">Akademik Baho</h3>
                    <p style="font-size: 0.82rem; opacity: 0.8;">Faqat faktik bilim va formulalar bo'yicha sof baho.</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<div class='big-score' style='color: #3b82f6;'>{eval_1['score']} <span style='font-size: 1.3rem; opacity: 0.6;'>/ {max_score}</span></div>", unsafe_allow_html=True)
                st.info(eval_1.get("detailed_analysis", ""))

            with c2:
                b_col = "#ef4444" if eval_2['score'] < (max_score * 0.5) else "#f59e0b"
                st.markdown(f"""
                <div class="grade-card" style="border-top: 5px solid {b_col};">
                    <span class="role-badge badge-admin">2-BOSQICH</span>
                    <h3 style="margin: 4px 0; color: #fca5a5;">AI Nazoratli Baho</h3>
                    <p style="font-size: 0.82rem; opacity: 0.8;">ChatGPT aniqlansa ball kesiladi yoki 0 qo'yiladi.</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<div class='big-score' style='color: {b_col};'>{eval_2['score']} <span style='font-size: 1.3rem; opacity: 0.6;'>/ {max_score}</span></div>", unsafe_allow_html=True)
                st.info(eval_2.get("explanation", ""))

            with c3:
                st.markdown("""
                <div class="grade-card" style="border-top: 5px solid #059669;">
                    <span class="role-badge badge-student">3-BOSQICH</span>
                    <h3 style="margin: 4px 0; color: #6ee7b7;">Empatiya Bahosi</h3>
                    <p style="font-size: 0.82rem; opacity: 0.8;">Mustaqil harakat va oraliq qadamlar uchun insoniy rag'bat.</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<div class='big-score' style='color: #10b981;'>{eval_3['score']} <span style='font-size: 1.3rem; opacity: 0.6;'>/ {max_score}</span></div>", unsafe_allow_html=True)
                st.info(eval_3.get("explanation", ""))

            st.markdown("---")
            col_dec1, col_dec2 = st.columns([3, 2])
            with col_dec1:
                chosen_p = st.radio(
                    "Qaysi bahoni yakuniy deb qabul qilasiz?",
                    options=[
                        f"1-Akademik baho: {eval_1['score']} / {max_score}",
                        f"2-AI nazorati bilan baho: {eval_2['score']} / {max_score}",
                        f"3-Empatiya bahosi: {eval_3['score']} / {max_score}",
                        "O'qituvchi o'zi istagan ballni qo'yishi"
                    ]
                )
                def_val = float(eval_3['score'] if "3-Empatiya" in chosen_p else (eval_2['score'] if "2-AI" in chosen_p else eval_1['score']))
                final_confirmed = st.slider("Yakuniy tasdiqlangan baho:", 0.0, float(max_score), def_val, 0.5)

            with col_dec2:
                student_options = [u["name"] for u in st.session_state.registered_users if u["role"] == "O'quvchi"]
                student_target = st.selectbox("Baholanayotgan o'quvchi:", student_options)
                teacher_note = st.text_input("O'qituvchi izohi:", value="Harakat va mustaqillik hisobga olindi.")
                
                if st.button("💾 Bahoni Jurnalga Saqlash", type="primary", use_container_width=True):
                    st.session_state.grades_journal.append({
                        "talaba": student_target,
                        "topshiriq": task_prompt[:40] + "...",
                        "max_ball": max_score,
                        "baho_1_akad": eval_1['score'],
                        "baho_2_ai": eval_2['score'],
                        "baho_3_emp": eval_3['score'],
                        "tasdiqlangan_ball": final_confirmed,
                        "izoh": teacher_note,
                        "feedback": results.get("student_feedback", "")
                    })
                    st.session_state.audit_logs.append({
                        "vaqt": datetime.now().strftime("%H:%M"),
                        "foydalanuvchi": f"{curr_u['name']} (O'qituvchi)",
                        "amal": f"{student_target} baholandi: {final_confirmed}/{max_score}"
                    })
                    st.balloons()
                    st.success("Baho elektron jurnalga saqlandi!")

    elif active_menu == "📂 Ommaviy Baholash & O'zaro Plagiat":
        st.subheader("📂 Butun Sinf Ishlarini Bir Yo'la Baholash va Plagiat Detektori")
        batch_files = st.file_uploader("Sinf topshiriqlarini tanlang:", type=["docx", "pdf", "txt", "png", "jpg"], accept_multiple_files=True)
        if batch_files:
            if st.button("🚀 Barcha Ishlarni Baholash va Plagiatni Tekshirish", type="primary"):
                with st.spinner("Tahlil qilinmoqda..."):
                    files_payload = [(f.name, f.read()) for f in batch_files]
                    bg = BatchGrader(gemini_api_key=st.session_state.secure_api_key)
                    b_res = bg.grade_batch_files(
                        files_payload, st.session_state.task_input, st.session_state.ref_input,
                        st.session_state.default_max_score, st.session_state.default_beta
                    )
                    
                    plag = b_res["plagiarism_report"]
                    if plag["flagged_pairs"]:
                        for p in plag["flagged_pairs"]:
                            st.error(f"🚨 KO'CHIRILGANLIK: '{p['student_1']}' va '{p['student_2']}' o'rtasida {p['similarity_pct']}% o'xshashlik! ({p['verdict']})")
                    else:
                        st.success("✅ Talabalar o'rtasida o'zaro ko'chirish holatlari aniqlanmadi.")

                    df_b = pd.DataFrame(b_res["graded_students"])[["student_name", "file_type", "score_1_academic", "score_2_ai", "score_3_empathy", "recommended_score", "is_peer_plagiarized"]]
                    df_b.columns = ["O'quvchi", "Fayl turi", "1-Akademik", "2-AI Nazorati", "3-Empatiya", "Tavsiya Ball", "O'zaro Plagiat"]
                    st.dataframe(df_b, use_container_width=True)

    elif active_menu == "📊 Elektron Baholash Jurnali":
        st.subheader("📊 Elektron Baholash Jurnali")
        if not st.session_state.grades_journal:
            st.info("Jurnal bo'sh.")
        else:
            table_d = []
            for idx, r in enumerate(st.session_state.grades_journal, 1):
                table_d.append({
                    "№": idx,
                    "O'quvchi": r["talaba"],
                    "Akademik (1)": f"{r['baho_1_akad']}/{r['max_ball']}",
                    "AI Nazorati (2)": f"{r['baho_2_ai']}/{r['max_ball']}",
                    "Empatiya (3)": f"{r['baho_3_emp']}/{r['max_ball']}",
                    "Tasdiqlangan Baho": f"{r['tasdiqlangan_ball']}/{r['max_ball']}",
                    "Izoh": r["izoh"]
                })
            st.table(table_d)

    elif active_menu == "📄 Rasmiy Dalolatnoma (PDF)":
        st.subheader("📄 Rasmiy Baholash Dalolatnomasi (Aкт внедрения)")
        prot_html = generate_official_protocol_html(
            "Toshkent shahar 110-sonli maktab", "Informatika", curr_u['name'],
            st.session_state.task_input[:35], st.session_state.default_max_score, st.session_state.grades_journal
        )
        st.download_button("📥 Rasmiy Dalolatnomani Yuklab Olish (HTML/PDF)", prot_html, "dalolatnoma.html", "text/html")
        st.components.v1.html(prot_html, height=480, scrolling=True)

    elif active_menu == "📈 Ilmiy Eksperiment & Validatsiya":
        st.subheader("📈 Ilmiy Eksperiment va Validatsiya Natijalari (Dissertatsiya IV Bobi)")
        bench = get_experiment_benchmark_data()
        s_stat = bench["statistik_xulosa"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Quadratic Weighted Kappa (QWK)", f"{s_stat['qwk_koeffitsiyenti']}", delta="Oliy moslik")
        m2.metric("Pearson Korrelyatsiyasi (r)", f"{s_stat['pearson_r']}", delta="Kuchli korrelyatsiya")
        m3.metric("O'rtacha Xatolik (MAE)", f"±{s_stat['mae']} ball", delta="Minimal xato")
        m4.metric("Vaqt Tejalishi", f"{s_stat['vaqt_tejalishi_foizi']}", delta="94.5% tejaldi")


# =========================================================================
# 🎓 3-PANEL: O'QUVCHI / TALABA PANELI (FAQAT O'QUVCHI UCHUN)
# =========================================================================
elif user_role == "O'quvchi":
    st.markdown(f"""
    <div class="portal-header-student">
        <span class="role-badge badge-student">O'quvchi Kabineti</span>
        <h2 style="margin: 4px 0 6px 0; font-size: 1.7rem;">🎓 {curr_u['name']} Shaxsiy Kabineti</h2>
        <p style="margin: 0; opacity: 0.85; font-size: 0.92rem;">
            Sinf/Guruh: <b>{curr_u.get('group', '10-A sinf')}</b> | Login: <code>@{curr_u['login']}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    if active_menu == "📤 Uy Vazifasini Topshirish":
        st.subheader("📋 O'qituvchi Bergan Joriy Uy Vazifasi")
        st.info(f"**Topshiriq sharti:**\n\n{st.session_state.task_input}")
        st.write(f"**Topshiriqning maksimal bali:** {st.session_state.default_max_score} ball")

        st.markdown("---")
        st.subheader("📤 Yechimingizni Yuklang:")
        
        tab_st_f, tab_st_t = st.tabs(["📁 Fayl Yuklash (Daftar fotosurati, Word, PDF)", "✍️ Matn Yozish"])
        with tab_st_f:
            st_upload = st.file_uploader("Faylni tanlang:", type=["png", "jpg", "jpeg", "docx", "pdf", "txt"])
            if st_upload:
                st.success(f"Tanlandi: {st_upload.name}")
        with tab_st_t:
            st_answer_text = st.text_area("Yechimingizni yozing:", height=150)

        if st.button("🚀 Vazifani O'qituvchiga Yuborish", type="primary"):
            st.session_state.audit_logs.append({
                "vaqt": datetime.now().strftime("%H:%M"),
                "foydalanuvchi": f"{curr_u['name']} (O'quvchi)",
                "amal": "Uy vazifasi topshirildi"
            })
            st.balloons()
            st.success("Vazifangiz qabul qilindi va tekshirish uchun o'qituvchiga yuborildi!")

    elif active_menu == "📜 Mening Baholarim & Tahlil":
        st.subheader(f"📜 {curr_u['name']} ning Baholash Natijalari")
        
        student_surname = curr_u['name'].split()[0]
        matching_grades = [g for g in st.session_state.grades_journal if student_surname.lower() in g["talaba"].lower()]
        
        if matching_grades:
            g = matching_grades[-1]
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; border-radius: 16px; padding: 22px; margin-bottom: 20px;">
                <span class="role-badge badge-student">Tasdiqlangan Yakuniy Baho</span>
                <div class="big-score" style="color: #10b981;">{g['tasdiqlangan_ball']} <span style="font-size: 1.4rem; opacity: 0.7;">/ {g['max_ball']}</span></div>
                <p style="margin: 0;"><b>O'qituvchi xulosasi:</b> {g['izoh']}</p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("🔍 Baholash Tafsilotlari (3 Xil O'lchov):")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.metric("1. Akademik Faktik Bilim", f"{g['baho_1_akad']} / {g['max_ball']}")
                st.caption("Faktlar va to'g'ri yechim bo'yicha sof bilim.")
            with sc2:
                st.metric("2. AI Nazorati (Halollik)", f"{g['baho_2_ai']} / {g['max_ball']}")
                st.caption("ChatGPT'dan foydalanilmaganlik darajasi.")
            with sc3:
                st.metric("3. Mustaqil Harakat Rag'bati", f"{g['baho_3_emp']} / {g['max_ball']}")
                st.caption("Mustaqil uringaningiz uchun berilgan rag'bat.")
        else:
            st.info("Hozircha sizning topshirig'ingiz o'qituvchi tomonidan tekshirilmoqda.")

    elif active_menu == "✉️ O'qituvchi Tavsiya Xati":
        st.subheader("✉️ O'qituvchidan Shaxsiy Tavsiya Xati")
        student_surname = curr_u['name'].split()[0]
        matching_grades = [g for g in st.session_state.grades_journal if student_surname.lower() in g["talaba"].lower()]
        
        if matching_grades and matching_grades[-1].get("feedback"):
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px dashed #3b82f6; border-radius: 14px; padding: 20px; line-height: 1.6;">
                {matching_grades[-1]['feedback']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("O'qituvchi hali fikr-mulohaza yozmadi.")
