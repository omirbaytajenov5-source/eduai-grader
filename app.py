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
    page_title="EduAI Grader - Intellektual Ta'lim Portali",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# MODERN CYBER-INDIGO & EMERALD DESIGN SYSTEM
# =========================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Yuqori E'lon Tasmasi (Cyber-Indigo & Emerald Gradient) */
    .ticker-banner {
        background: linear-gradient(100deg, #1e1b4b 0%, #312e81 30%, #0e7490 70%, #059669 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #ffffff;
        padding: 10px 22px;
        border-radius: 14px;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.2px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(14, 116, 144, 0.25);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .ticker-tag {
        background: rgba(16, 185, 129, 0.25);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 8px;
    }

    /* Statistik Kartochkalar (Metric Cards) */
    .metric-box-lms {
        background: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 22px 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 16px;
        border-bottom: 4px solid #10b981;
    }
    .metric-box-lms:hover {
        transform: translateY(-4px);
        box-shadow: 0 14px 30px -4px rgba(16, 185, 129, 0.2), 0 4px 15px rgba(99, 102, 241, 0.15);
        border-color: #cbd5e1;
    }
    .metric-box-title {
        font-size: 0.95rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-box-num {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }
    .metric-box-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 44px;
        height: 44px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }

    /* Guruh Kartochkalari (Class Grid Cards) */
    .class-card {
        background: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        margin-bottom: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .class-card:hover {
        transform: translateY(-4px);
        border-color: #6366f1;
        box-shadow: 0 14px 32px -4px rgba(99, 102, 241, 0.2);
    }
    .class-accent-bar {
        height: 4px;
        width: 100%;
        border-radius: 4px;
        margin-bottom: 14px;
    }
    .class-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 4px 0;
    }
    .class-subtitle {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .class-badge-pill {
        display: inline-block;
        background: #f1f5f9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Tugmalar dizayni */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 6px 14px;
        transition: all 0.2s ease;
    }

    /* Pastki Profil Kartasi */
    .user-footer-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 14px 16px;
        margin-top: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .user-avatar-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #10b981 0%, #06b6d4 50%, #6366f1 100%);
        color: white;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.35);
    }

    /* Baholash Natijalari (3D Grade Cards) */
    .grade-card {
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 16px;
    }
    .big-score {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# BAZADAN FOYDALANUVCHILARNI YUKLASH (DISK PERSISTENCE)
st.session_state.registered_users = load_users()

# TIZIMGA KIRGAN FOYDALANUVChI (SESSION)
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "teacher_classes" not in st.session_state:
    st.session_state.teacher_classes = [
        {
            "id": 1,
            "subject": "Veb dasturlash",
            "grade_level": "10-A",
            "class_info": "10-A • Butun sinf • 12 o'quvchi",
            "accent": "linear-gradient(90deg, #6366f1, #3b82f6)",
            "badge_color": "#e0e7ff",
            "room": "304-xona",
            "syllabus": ["HTML5/CSS3 asoslari", "Flexbox va Grid", "JavaScript DOM manipulyatsiyasi", "AI bilan kodlash"]
        },
        {
            "id": 2,
            "subject": "Tarmoq texnologiyalari",
            "grade_level": "10-A",
            "class_info": "10-A • Butun sinf • 10 o'quvchi",
            "accent": "linear-gradient(90deg, #0d9488, #10b981)",
            "badge_color": "#ccfbf1",
            "room": "Server xonasi",
            "syllabus": ["OSI va TCP/IP modellari", "IP adreslash & Subnetting", "Router & Switch sozlash", "Kiberxavfsizlik asoslari"]
        },
        {
            "id": 3,
            "subject": "Sun'iy intellekt & Data",
            "grade_level": "10-A",
            "class_info": "10-A • Butun sinf • 7 o'quvchi",
            "accent": "linear-gradient(90deg, #8b5cf6, #ec4899)",
            "badge_color": "#f3e8ff",
            "room": "AI Laboratoriyasi",
            "syllabus": ["Mashinali o'rganish kirish", "NLP va Matn tahlili", "LLM va Neyrotarmoqlar", "3D Baholash algoritmlari"]
        },
        {
            "id": 4,
            "subject": "Mobil dasturlash",
            "grade_level": "10-A",
            "class_info": "10-A • Butun sinf • 15 o'quvchi",
            "accent": "linear-gradient(90deg, #f43f5e, #fb923c)",
            "badge_color": "#fce7f3",
            "room": "205-xona",
            "syllabus": ["Flutter arxitekturasi", "Widgetlar va State Management", "API integratsiyasi", "Mobil UI/UX dizayn"]
        },
        {
            "id": 5,
            "subject": "Informatika va AT",
            "grade_level": "8-C",
            "class_info": "8-C • Butun sinf • 11 o'quvchi",
            "accent": "linear-gradient(90deg, #10b981, #06b6d4)",
            "badge_color": "#dcfce7",
            "room": "102-xona",
            "syllabus": ["Axborot xavfsizligi", "Elektron jadvallar (Excel)", "Ma'lumotlar bazasi (SQL)", "Algoritmlar nazariyasi"]
        },
        {
            "id": 6,
            "subject": "Python algoritmlari",
            "grade_level": "8-A",
            "class_info": "8-A • Butun sinf • 12 o'quvchi",
            "accent": "linear-gradient(90deg, #f59e0b, #eab308)",
            "badge_color": "#fef3c7",
            "room": "Kompyuter sinfi",
            "syllabus": ["Funksiyalar va Rekursiya", "Ro'yxat va Lug'atlar", "OOP tamoyillari", "Fayllar bilan ishlash"]
        }
    ]

if "class_modal_view" not in st.session_state:
    st.session_state.class_modal_view = None

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
        {"vaqt": "14:20", "foydalanuvchi": "Omirbay Tajenov", "amal": "Tizimga kirdi (Login)"},
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
            "izoh": "Mustaqil harakat va oraliq qadamlar uchun rag'batlantirildi.",
            "feedback": "Aziz Jasur! Oraliq hisob-kitoblaringiz va samimiy urinishingiz ajoyib. Xatolar ustida ishlashda davom eting!"
        }
    ]

# =========================================================================
# KIRISH OYNASI (LOGIN SCREEN)
# =========================================================================
if st.session_state.current_user is None:
    st.markdown("""
    <div style="max-width: 650px; margin: 40px auto 20px auto; text-align: center;">
        <h1 style="font-size: 2.4rem; font-weight: 800; background: linear-gradient(135deg, #6366f1 0%, #06b6d4 50%, #10b981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">
            🎓 EduAI Grader
        </h1>
        <p style="font-size: 1.05rem; opacity: 0.85; color: #cbd5e1;">
            Intellektual Ta'lim va 3D Baholash Platformasi — Tizimga Kirish
        </p>
    </div>
    """, unsafe_allow_html=True)

    login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
    with login_col2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 20px; padding: 28px; box-shadow: 0 12px 35px rgba(0,0,0,0.45);">
            <h3 style="margin-top: 0; text-align: center; color: white;">🔐 Akkauntga Kirish</h3>
        """, unsafe_allow_html=True)
        
        input_login = st.text_input("Foydalanuvchi Logini:", placeholder="omirbaytajenov5@gmail.com yoki teacher yoki jasur")
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
        st.caption("⚡ **Tezkor kirish tugmalari:**")
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
# ASOSIY DASTUR: KIRILGAN FOYDALANUVChI
# =========================================================================
curr_u = st.session_state.current_user
user_role = curr_u["role"]
initials = "".join([part[0].upper() for part in curr_u['name'].split()[:2]])

# SIDEBAR: MODERN CYBER-INDIGO & EMERALD MENYU
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 6px 0 18px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 16px;">
        <span style="font-size: 2rem;">🎓</span>
        <div>
            <h3 style="margin: 0; font-size: 1.3rem; font-weight: 800; background: linear-gradient(135deg, #10b981 0%, #06b6d4 50%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">EduAI</h3>
            <span style="font-size: 0.72rem; color: #10b981; font-weight: 700; letter-spacing: 0.5px;">CYBER-INTELLIGENCE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Rolga mos menyu
    if user_role == "Administrator":
        st.caption("🛡️ ADMINISTRATOR MENYUSI")
        active_menu = st.radio(
            "Bo'limlar:",
            [
                "🏠 Bosh sahifa & Monitoring",
                "➕ Yangi Foydalanuvchi Qo'shish",
                "👥 Akkauntlar Boshqaruvi",
                "🔐 Global API & Xavfsizlik",
                "📋 Tizim Audit Loglari"
            ],
            label_visibility="collapsed"
        )
    elif user_role == "O'qituvchi":
        st.caption("🧑‍🏫 O'QITUVChI MENYUSI")
        active_menu = st.radio(
            "Bo'limlar:",
            [
                "🏠 Bosh sahifa (Dashboard)",
                "🏫 Sinflar & Guruhlar Boshqaruvi",
                "📅 Taqvim & Dars Jadvali",
                "📝 3D Baholash Laboratoriyasi",
                "📂 Ommaviy Baholash & Plagiat",
                "📊 Elektron Baholash Jurnali",
                "📄 Rasmiy Dalolatnoma (PDF)",
                "📈 Ilmiy Eksperiment (IV Bob)"
            ],
            label_visibility="collapsed"
        )
    else: # O'quvchi
        st.caption("🎓 O'QUVChI MENYUSI")
        active_menu = st.radio(
            "Bo'limlar:",
            [
                "🏠 Bosh sahifa & Vazifalar",
                "📤 Uy Vazifasini Topshirish",
                "📜 Mening Baholarim & Tahlil",
                "✉️ O'qituvchi Tavsiya Xati"
            ],
            label_visibility="collapsed"
        )

    st.markdown("---")

    # Pastki Profil qismi
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
        <div class="user-avatar-circle">{initials}</div>
        <div>
            <div style="font-size: 0.95rem; font-weight: 700; color: white;">{curr_u['name']}</div>
            <div style="font-size: 0.75rem; color: #34d399; font-weight: 600;">{user_role}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Chiqish", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.class_modal_view = None
        st.rerun()


# =========================================================================
# 🧑‍🏫 O'QITUVCHI PANELI
# =========================================================================
if user_role == "O'qituvchi":
    # 1. YUQORI E'LON TASMASI (CYBER TICKER RIBBON)
    st.markdown("""
    <div class="ticker-banner">
        <div style="display: flex; align-items: center;">
            <span class="ticker-tag">AI LIVE</span>
            <span>📢 <b>Xush kelibsiz!</b> EduAI Grader ta'lim platformasiga xush kelibsiz! Bugungi mashg'ulotlaringizda omad tilaymiz!</span>
        </div>
        <div style="opacity: 0.9; font-size: 0.85rem; font-weight: 600; display: flex; gap: 14px; align-items: center;">
            <span>🇺🇿 O'zbekcha ▾</span>
            <span>🔔 Bildirishnomalar (2)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # A. BOSH SAHIFA: GURUHLAR VA STATISTIKA (GILT.UZ STRUKTURASI + CYBER PALITRA)
    if active_menu == "🏠 Bosh sahifa (Dashboard)":
        col_th1, col_th2 = st.columns([4, 1.2])
        with col_th1:
            st.markdown("""
            <h2 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: white;">O'qituvchi paneli</h2>
            <p style="margin: 4px 0 20px 0; color: #94a3b8; font-size: 0.95rem;">Guruhlaringiz — jurnal, uy vazifalari va 3D sun'iy intellekt tahlili shu yerda.</p>
            """, unsafe_allow_html=True)
        with col_th2:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("➕ Yangi Dars Qo'shish →", type="primary", use_container_width=True):
                st.session_state.show_add_class_box = True

        # 3 TA STATISTIK KARTOChKA (METRIC CARDS)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("""
            <div class="metric-box-lms" style="border-bottom-color: #6366f1;">
                <div class="metric-box-title">Guruhlarim</div>
                <div class="metric-box-num">6</div>
                <div class="metric-box-badge" style="background: #e0e7ff; color: #4338ca;">📚</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown("""
            <div class="metric-box-lms" style="border-bottom-color: #10b981;">
                <div class="metric-box-title">O'quvchilar</div>
                <div class="metric-box-num">78</div>
                <div class="metric-box-badge" style="background: #dcfce7; color: #047857;">🎓</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            unreviewed_count = max(1, 14 - len(st.session_state.grades_journal))
            st.markdown(f"""
            <div class="metric-box-lms" style="border-bottom-color: #06b6d4;">
                <div class="metric-box-title">Baholanmagan vazifa</div>
                <div class="metric-box-num">{unreviewed_count}</div>
                <div style="font-size: 0.8rem; color: #0891b2; font-weight: 600; margin-top: 4px;">Tekshirishni kutmoqda</div>
                <div class="metric-box-badge" style="background: #cffafe; color: #0e7490;">⏳</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h3 style='margin: 18px 0 16px 0; font-size: 1.35rem; font-weight: 800; color: white;'>Mening Guruhlarim</h3>", unsafe_allow_html=True)

        # 6 TA SINF / FAN KARTOChKASI (GRID)
        cls_grid1, cls_grid2, cls_grid3 = st.columns(3)
        cols_cycle = [cls_grid1, cls_grid2, cls_grid3]

        for idx, item in enumerate(st.session_state.teacher_classes):
            with cols_cycle[idx % 3]:
                st.markdown(f"""
                <div class="class-card">
                    <div class="class-accent-bar" style="background: {item['accent']};"></div>
                    <div class="class-title">{item['subject']}</div>
                    <div class="class-subtitle">
                        <span>{item['class_info']}</span>
                        <span class="class-badge-pill">{item['room']}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Kartochka ichidagi tezkor harakat tugmalari
                btn_c1, btn_c2, btn_c3, btn_c4 = st.columns(4)
                with btn_c1:
                    if st.button("O'quvchilar", key=f"btn_u_{item['id']}", use_container_width=True):
                        st.session_state.class_modal_view = {"type": "students", "class": item}
                with btn_c2:
                    if st.button("Jurnal", key=f"btn_j_{item['id']}", use_container_width=True):
                        st.session_state.class_modal_view = {"type": "journal", "class": item}
                with btn_c3:
                    if st.button("Reja", key=f"btn_p_{item['id']}", use_container_width=True):
                        st.session_state.class_modal_view = {"type": "plan", "class": item}
                with btn_c4:
                    if st.button("✨ Tahlil", key=f"btn_ai_{item['id']}", type="primary", use_container_width=True):
                        st.session_state.task_input = f"{item['subject']} fanidan uy vazifasi va amaliy laboratoriya topshirig'i."
                        st.session_state.class_modal_view = {"type": "grading_redirect", "class": item}

                st.markdown("</div>", unsafe_allow_html=True)

        # TANLANGAN HARAKATNING INTERAKTIV OYNASI (DRAWER/POPUP)
        if st.session_state.class_modal_view:
            mv = st.session_state.class_modal_view
            cls_item = mv["class"]
            st.markdown("---")
            
            if mv["type"] == "students":
                st.info(f"👥 **{cls_item['subject']} ({cls_item['grade_level']})** — Biriktirilgan o'quvchilar ro'yxati:")
                st_data = [
                    {"№": 1, "F.I.Sh": "Azizov Jasur", "Holat": "Faol", "Oxirgi topshiriq": "Topshirdi", "Ball": "9.1/10"},
                    {"№": 2, "F.I.Sh": "Karimov Dilshod", "Holat": "Faol", "Oxirgi topshiriq": "Kutilmoqda", "Ball": "—"},
                    {"№": 3, "F.I.Sh": "Nazarova Nigora", "Holat": "Faol", "Oxirgi topshiriq": "Topshirdi", "Ball": "8.8/10"},
                    {"№": 4, "F.I.Sh": "Sobirov Alisher", "Holat": "Faol", "Oxirgi topshiriq": "Topshirdi", "Ball": "9.5/10"},
                    {"№": 5, "F.I.Sh": "Rustamova Laylo", "Holat": "Faol", "Oxirgi topshiriq": "Topshirdi", "Ball": "7.9/10"}
                ]
                st.dataframe(pd.DataFrame(st_data), use_container_width=True)
                if st.button("Yopish ✖️", key="close_students"):
                    st.session_state.class_modal_view = None
                    st.rerun()

            elif mv["type"] == "journal":
                st.success(f"📊 **{cls_item['subject']}** — Guruh baholash jurnali:")
                st.table(pd.DataFrame([
                    {"Mavzu": "1-Amaliy mashg'ulot", "O'rtacha ball": "8.7", "AI Plagiat nazorati": "0 ta holat", "Topshirganlar": "12/12"},
                    {"Mavzu": "2-Laboratoriya ishi", "O'rtacha ball": "8.2", "AI Plagiat nazorati": "1 ta tekshirildi", "Topshirganlar": "11/12"}
                ]))
                if st.button("Yopish ✖️", key="close_journal"):
                    st.session_state.class_modal_view = None
                    st.rerun()

            elif mv["type"] == "plan":
                st.warning(f"📑 **{cls_item['subject']}** — O'quv dasturi va mavzular rejasi (Syllabus):")
                for s_idx, topic in enumerate(cls_item.get("syllabus", []), 1):
                    st.write(f"**{s_idx}-Mavzu:** {topic}")
                if st.button("Yopish ✖️", key="close_plan"):
                    st.session_state.class_modal_view = None
                    st.rerun()

            elif mv["type"] == "grading_redirect":
                st.success(f"🎯 **{cls_item['subject']}** fani bo'yicha baholash laboratoriyasiga ma'lumot uzatildi! Chap menyudan **'3D Baholash Laboratoriyasi'** sahifasiga o'ting.")
                if st.button("Yopish ✖️", key="close_redirect"):
                    st.session_state.class_modal_view = None
                    st.rerun()

    # B. SINFLAR & GURUHLAR BOSHQARUVI (GILT.UZ SINFLAR BO'LIMI)
    elif active_menu == "🏫 Sinflar & Guruhlar Boshqaruvi":
        st.subheader("🏫 Mening Sinflarim va Guruhlar Ro'yxati")
        
        c_add1, c_add2 = st.columns([3, 1])
        with c_add1:
            st.write("Sizga biriktirilgan barcha faol sinflar va dars yuklamalari:")
        with c_add2:
            with st.expander("➕ Yangi Guruh Qo'shish"):
                n_subj = st.text_input("Fan nomi:", placeholder="Masalan: Robototexnika")
                n_class = st.text_input("Sinf:", placeholder="Masalan: 11-A")
                n_room = st.text_input("Xona:", placeholder="Masalan: 401-xona")
                if st.button("Saqlash", type="primary"):
                    st.session_state.teacher_classes.append({
                        "id": len(st.session_state.teacher_classes) + 1,
                        "subject": n_subj,
                        "grade_level": n_class,
                        "class_info": f"{n_class} • Butun sinf • 14 o'quvchi",
                        "accent": "linear-gradient(90deg, #10b981, #06b6d4)",
                        "badge_color": "#dcfce7",
                        "room": n_room,
                        "syllabus": ["1-Mavzu: Kirish", "2-Mavzu: Amaliyot"]
                    })
                    st.success("Yangi guruh qo'shildi!")
                    st.rerun()

        classes_df = []
        for c in st.session_state.teacher_classes:
            classes_df.append({
                "ID": c["id"],
                "Fan": c["subject"],
                "Sinf": c["grade_level"],
                "Tafsilot": c["class_info"],
                "Dars Xonasi": c["room"],
                "Mavzular soni": len(c.get("syllabus", []))
            })
        st.dataframe(pd.DataFrame(classes_df), use_container_width=True)

    # C. TAQVIM & DARS JADVALI (GILT.UZ TAQVIM BO'LIMI)
    elif active_menu == "📅 Taqvim & Dars Jadvali":
        st.subheader("📅 O'qituvchining Haftalik Dars Jadvali va Rejasi")
        schedule_data = [
            {"Kun": "Dushanba", "Vaqt": "08:30 - 09:50", "Fan": "Veb dasturlash", "Sinf": "10-A", "Xona": "304", "Holat": "✅ O'tildi"},
            {"Kun": "Dushanba", "Vaqt": "10:00 - 11:20", "Fan": "Tarmoq texnologiyalari", "Sinf": "10-A", "Xona": "Server", "Holat": "✅ O'tildi"},
            {"Kun": "Seshanba", "Vaqt": "08:30 - 09:50", "Fan": "Informatika va AT", "Sinf": "8-C", "Xona": "102", "Holat": "🕒 Navbatdagi"},
            {"Kun": "Chorshanba", "Vaqt": "11:30 - 12:50", "Fan": "Python algoritmlari", "Sinf": "8-A", "Xona": "Komp", "Holat": "📝 3D Baholash Topshirig'i"},
            {"Kun": "Payshanba", "Vaqt": "08:30 - 09:50", "Fan": "Sun'iy intellekt & Data", "Sinf": "10-A", "Xona": "AI Lab", "Holat": "Rejalashtirilgan"},
            {"Kun": "Juma", "Vaqt": "10:00 - 11:20", "Fan": "Mobil dasturlash", "Sinf": "10-A", "Xona": "205", "Holat": "Rejalashtirilgan"}
        ]
        st.dataframe(pd.DataFrame(schedule_data), use_container_width=True)

    # D. 3D BAHOLASH LABORATORIYASI
    elif active_menu == "📝 3D Baholash Laboratoriyasi":
        st.subheader("📝 3D Baholash Laboratoriyasi (Yakka Tartibda)")
        col_setup1, col_setup2 = st.columns([2, 1])
        with col_setup1:
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
        st.subheader("O'quvchi Javobini Qabul Qilish")
        tab_f, tab_t = st.tabs(["📁 Fayl Yuklash (Word, PDF, TXT, Rasm)", "✍️ Matn Yozish"])
        with tab_f:
            uploaded_file = st.file_uploader("Faylni tanlang:", type=["docx", "pdf", "txt", "png", "jpg", "jpeg", "webp"])
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                extracted_text, img_obj, file_type = parse_uploaded_file(file_bytes, uploaded_file.name)
                norm_text = normalize_uzbek_text(extracted_text)
                st.session_state.student_text = norm_text if norm_text else st.session_state.student_text
                st.session_state.uploaded_image = img_obj
                st.success(f"Yuklandi: {uploaded_file.name} ({file_type})")
                if img_obj:
                    st.image(img_obj, caption="Daftar sahifasi", width=360)

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
                st.markdown(f"""
                <div class="grade-card" style="border-top: 5px solid #6366f1;">
                    <div style="font-weight: 700; color: #818cf8;">1-BOSQICH</div>
                    <h3 style="margin: 4px 0; color: white;">Akademik Baho</h3>
                    <div class="big-score" style="color: #818cf8;">{eval_1['score']} <span style='font-size: 1.2rem; opacity: 0.6;'>/ {max_score}</span></div>
                    <p style="font-size: 0.85rem; color: #cbd5e1;">Faktik bilim va to'g'ri formulalar.</p>
                </div>
                """, unsafe_allow_html=True)
                st.info(eval_1.get("detailed_analysis", ""))

            with c2:
                b_col = "#ef4444" if eval_2['score'] < (max_score * 0.5) else "#06b6d4"
                st.markdown(f"""
                <div class="grade-card" style="border-top: 5px solid {b_col};">
                    <div style="font-weight: 700; color: {b_col};">2-BOSQICH</div>
                    <h3 style="margin: 4px 0; color: white;">AI Nazoratli Baho</h3>
                    <div class="big-score" style="color: {b_col};">{eval_2['score']} <span style='font-size: 1.2rem; opacity: 0.6;'>/ {max_score}</span></div>
                    <p style="font-size: 0.85rem; color: #cbd5e1;">ChatGPT aniqlansa ball kesiladi yoki 0 qo'yiladi.</p>
                </div>
                """, unsafe_allow_html=True)
                st.info(eval_2.get("explanation", ""))

            with c3:
                st.markdown(f"""
                <div class="grade-card" style="border-top: 5px solid #10b981;">
                    <div style="font-weight: 700; color: #34d399;">3-BOSQICH</div>
                    <h3 style="margin: 4px 0; color: white;">Empatiya Bahosi</h3>
                    <div class="big-score" style="color: #34d399;">{eval_3['score']} <span style='font-size: 1.2rem; opacity: 0.6;'>/ {max_score}</span></div>
                    <p style="font-size: 0.85rem; color: #cbd5e1;">Mustaqil harakat va qadamlar uchun insoniy rag'bat.</p>
                </div>
                """, unsafe_allow_html=True)
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
                    st.balloons()
                    st.success("Baho elektron jurnalga saqlandi!")

    # E. OMMAVIY BAHOLASH & O'ZARO PLAGIAT
    elif active_menu == "📂 Ommaviy Baholash & Plagiat":
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

    # F. ELEKTRON BAHOLASH JURNALI
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

    # G. RASMIY DALOLATNOMA
    elif active_menu == "📄 Rasmiy Dalolatnoma (PDF)":
        st.subheader("📄 Rasmiy Baholash Dalolatnomasi (Aкт внедрения)")
        prot_html = generate_official_protocol_html(
            "Toshkent shahar 110-sonli maktab", "Informatika", curr_u['name'],
            st.session_state.task_input[:35], st.session_state.default_max_score, st.session_state.grades_journal
        )
        st.download_button("📥 Rasmiy Dalolatnomani Yuklab Olish (HTML/PDF)", prot_html, "dalolatnoma.html", "text/html")
        st.components.v1.html(prot_html, height=480, scrolling=True)

    # H. ILMIY EKSPERIMENT
    elif active_menu == "📈 Ilmiy Eksperiment (IV Bob)":
        st.subheader("📈 Ilmiy Eksperiment va Validatsiya Natijalari (Dissertatsiya IV Bobi)")
        bench = get_experiment_benchmark_data()
        s_stat = bench["statistik_xulosa"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Quadratic Weighted Kappa (QWK)", f"{s_stat['qwk_koeffitsiyenti']}", delta="Oliy moslik")
        m2.metric("Pearson Korrelyatsiyasi (r)", f"{s_stat['pearson_r']}", delta="Kuchli korrelyatsiya")
        m3.metric("O'rtacha Xatolik (MAE)", f"±{s_stat['mae']} ball", delta="Minimal xato")
        m4.metric("Vaqt Tejalishi", f"{s_stat['vaqt_tejalishi_foizi']}", delta="94.5% tejaldi")


# =========================================================================
# 🛡️ ADMINISTRATOR PANELI
# =========================================================================
elif user_role == "Administrator":
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%); border-left: 5px solid #10b981; border-radius: 16px; padding: 18px 24px; margin-bottom: 22px;">
        <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">Administrator Paneli</span>
        <h2 style="margin: 6px 0 6px 0; font-size: 1.7rem; color: white;">🛡️ Administrator Boshqaruv Markazi</h2>
        <p style="margin: 0; opacity: 0.85; font-size: 0.92rem; color: #cbd5e1;">
            Faqat admin yangi o'qituvchi va o'quvchilarni <b>Login va Parol</b> bilan ro'yxatdan o'tkazishi, akkauntlarni boshqarishi mumkin.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if active_menu == "➕ Yangi Foydalanuvchi Qo'shish":
        st.subheader("➕ Yangi O'qituvchi yoki O'quvchi Qo'shish")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            add_role = st.selectbox("1. Roli:", ["O'qituvchi", "O'quvchi"])
            add_name = st.text_input("2. F.I.Sh:", placeholder="Masalan: Rustamov Bekzod")
            add_group = st.text_input("3. Sinf / Kafedra:", placeholder="Masalan: 10-B sinf")
            add_email = st.text_input("4. E-mail:", placeholder="bekzod@eduai.uz")

        with col_f2:
            suggested_login = (add_name.split()[0].lower() + ("_teacher" if add_role == "O'qituvchi" else "_student")) if add_name else ""
            add_login = st.text_input("5. Login (Username):", value=suggested_login)
            default_pwd = "".join(random.choices(string.ascii_letters + string.digits, k=8))
            add_password = st.text_input("6. Parol:", value=default_pwd)

            if st.button("🎲 Yangi Parol Generatsiya Qilish"):
                st.rerun()

            if st.button("💾 Foydalanuvchini Saqlash", type="primary", use_container_width=True):
                if not add_name or not add_login or not add_password:
                    st.error("Majburiy maydonlarni to'ldiring!")
                else:
                    success, msg = add_user(add_name, add_role, add_login, add_password, add_email, add_group)
                    if success:
                        st.session_state.registered_users = load_users()
                        st.balloons()
                        st.success(f"✅ Yangi {add_role.lower()} saqlandi! Login: `{add_login}` | Parol: `{add_password}`")
                    else:
                        st.error(msg)

    elif active_menu == "👥 Akkauntlar Boshqaruvi":
        st.subheader("👥 Ro'yxatdan O'tgan Akkauntlar")
        show_p = st.checkbox("👁️ Parollarni ko'rsatish", value=False)
        user_rows = []
        for u in st.session_state.registered_users:
            user_rows.append({
                "ID": u["id"],
                "F.I.Sh": u["name"],
                "Roli": u["role"],
                "Sinf/Guruh": u.get("group", ""),
                "Login": u["login"],
                "Parol": u["password"] if show_p else "••••••••",
                "E-mail": u["email"]
            })
        st.dataframe(pd.DataFrame(user_rows), use_container_width=True)

    elif active_menu == "🏠 Bosh sahifa & Monitoring":
        c_m1, c_m2, c_m3 = st.columns(3)
        teachers_count = len([u for u in st.session_state.registered_users if u["role"] == "O'qituvchi"])
        students_count = len([u for u in st.session_state.registered_users if u["role"] == "O'quvchi"])
        c_m1.metric("O'qituvchilar", f"{teachers_count} nafar")
        c_m2.metric("O'quvchilar", f"{students_count} nafar")
        c_m3.metric("Baholangan Ishlar", f"{len(st.session_state.grades_journal)} ta")

    elif active_menu == "🔐 Global API & Xavfsizlik":
        st.subheader("🔐 Google Gemini API Kaliti")
        api_val = st.text_input("API Kaliti:", value=st.session_state.secure_api_key, type="password")
        if st.button("Saqlash", type="primary"):
            st.session_state.secure_api_key = api_val.strip()
            st.success("API saqlandi!")

    elif active_menu == "📋 Tizim Audit Loglari":
        st.subheader("📋 Tizim Audit Loglari")
        st.table(pd.DataFrame(st.session_state.audit_logs))


# =========================================================================
# 🎓 O'QUVCHI PANELI
# =========================================================================
elif user_role == "O'quvchi":
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%); border-left: 5px solid #06b6d4; border-radius: 16px; padding: 18px 24px; margin-bottom: 22px;">
        <span style="background: rgba(6, 182, 212, 0.2); color: #22d3ee; padding: 3px 10px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">O'quvchi Kabineti</span>
        <h2 style="margin: 6px 0 6px 0; font-size: 1.7rem; color: white;">🎓 {curr_u['name']} Shaxsiy Kabineti</h2>
        <p style="margin: 0; opacity: 0.85; font-size: 0.92rem; color: #cbd5e1;">
            Sinf: <b>{curr_u.get('group', '10-A sinf')}</b> | Login: <code>@{curr_u['login']}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    if active_menu == "🏠 Bosh sahifa & Vazifalar":
        st.subheader("📚 Mening Darslarim va Faol Topshiriqlar")
        st.info("Sizga biriktirilgan fanlar bo'yicha yangi topshiriqlar mavjud. Chap menyudan 'Uy Vazifasini Topshirish' bo'limiga o'ting.")
        c_st1, c_st2 = st.columns(2)
        with c_st1:
            st.metric("O'rtacha Baho", "8.9 / 10", delta="Ijobiy o'sish")
        with c_st2:
            st.metric("Tekshirilgan Ishlar", f"{len(st.session_state.grades_journal)} ta")

    elif active_menu == "📤 Uy Vazifasini Topshirish":
        st.subheader("📋 Topshiriq Sharti")
        st.info(st.session_state.task_input)
        st_upload = st.file_uploader("Yechim fotosurati yoki hujjat:", type=["png", "jpg", "jpeg", "docx", "pdf", "txt"])
        st_text = st.text_area("Yoki yechimingizni yozing:", height=150)
        if st.button("🚀 Vazifani Topshirish", type="primary"):
            st.balloons()
            st.success("Vazifa muvaffaqiyatli topshirildi!")

    elif active_menu == "📜 Mening Baholarim & Tahlil":
        st.subheader("📜 Mening Baholarim")
        student_surname = curr_u['name'].split()[0]
        matching_grades = [g for g in st.session_state.grades_journal if student_surname.lower() in g["talaba"].lower()]
        if matching_grades:
            g = matching_grades[-1]
            st.metric("Tasdiqlangan Baho", f"{g['tasdiqlangan_ball']} / {g['max_ball']}")
            st.write(f"**Izoh:** {g['izoh']}")
        else:
            st.info("Hozircha vazifangiz tekshirilmoqda.")

    elif active_menu == "✉️ O'qituvchi Tavsiya Xati":
        st.subheader("✉️ O'qituvchidan Shaxsiy Tavsiya Xati")
        student_surname = curr_u['name'].split()[0]
        matching_grades = [g for g in st.session_state.grades_journal if student_surname.lower() in g["talaba"].lower()]
        if matching_grades and matching_grades[-1].get("feedback"):
            st.info(matching_grades[-1]["feedback"])
        else:
            st.info("O'qituvchi hali tavsiya yozmadi.")
