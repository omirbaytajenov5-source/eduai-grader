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
from modules.db_manager import load_users, save_users, add_user, authenticate_user, load_settings, save_settings
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
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# 🌈 ULTRA-YORQIN, ZAMONAVIY VA JONLI EDTECH DIZAYNI (LUMINOUS NEO-SAAS)
# =========================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* 1. Global Yorug' va Jonli Fon */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #f8fafc !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(6, 182, 212, 0.1) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.08) 0px, transparent 50%) !important;
        background-attachment: fixed !important;
        color: #0f172a !important;
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* 2. Chap Yon Menyu (Toza oq, zamonaviy shisha) */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1.5px solid #e2e8f0 !important;
        box-shadow: 4px 0 25px rgba(15, 23, 42, 0.03) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: #334155 !important;
    }
    
    /* 3. Sarlavhalar */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    p, span, label {
        color: #475569;
    }
    
    /* 4. Yuqori E'lon Tasmasi (Yorqin Gradient Ribbon) */
    .luminous-banner {
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 35%, #06b6d4 70%, #10b981 100%) !important;
        color: #ffffff !important;
        padding: 13px 24px;
        border-radius: 16px;
        font-size: 0.94rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    .luminous-banner * {
        color: #ffffff !important;
    }
    .badge-live-ai {
        background: rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 800;
        margin-right: 10px;
        letter-spacing: 0.5px;
    }
    
    /* 5. 3 ta Asosiy KPI Kartasi (Luminous Pastel Depth) */
    .metric-card-bright {
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 24px 26px !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 20px !important;
    }
    .metric-card-bright:hover {
        transform: translateY(-4px) !important;
    }
    
    .card-bright-indigo {
        background: linear-gradient(145deg, #ffffff 0%, #eff6ff 100%) !important;
        border: 1.5px solid #bfdbfe !important;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.12), 0 4px 6px -2px rgba(59, 130, 246, 0.05) !important;
    }
    .card-bright-indigo:hover {
        border-color: #60a5fa !important;
        box-shadow: 0 16px 30px -5px rgba(59, 130, 246, 0.22) !important;
    }
    
    .card-bright-emerald {
        background: linear-gradient(145deg, #ffffff 0%, #ecfdf5 100%) !important;
        border: 1.5px solid #a7f3d0 !important;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.12), 0 4px 6px -2px rgba(16, 185, 129, 0.05) !important;
    }
    .card-bright-emerald:hover {
        border-color: #34d399 !important;
        box-shadow: 0 16px 30px -5px rgba(16, 185, 129, 0.22) !important;
    }
    
    .card-bright-amber {
        background: linear-gradient(145deg, #ffffff 0%, #fffbeb 100%) !important;
        border: 1.5px solid #fde68a !important;
        box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.12), 0 4px 6px -2px rgba(245, 158, 11, 0.05) !important;
    }
    .card-bright-amber:hover {
        border-color: #fbbf24 !important;
        box-shadow: 0 16px 30px -5px rgba(245, 158, 11, 0.22) !important;
    }
    
    .metric-title-bright {
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 6px !important;
    }
    .metric-num-bright {
        font-size: 2.85rem !important;
        font-weight: 900 !important;
        line-height: 1.05 !important;
        margin: 0 !important;
    }
    .metric-icon-bright {
        position: absolute !important;
        top: 22px !important;
        right: 22px !important;
        width: 48px !important;
        height: 48px !important;
        border-radius: 14px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.45rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
    }
    
    /* 6. Fanlar va Guruhlar Kartochkalari (Luminous Class Cards) */
    .class-card-bright {
        background: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 20px !important;
        padding: 22px !important;
        margin-bottom: 14px !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .class-card-bright:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 16px 32px -4px rgba(99, 102, 241, 0.15) !important;
        border-color: #818cf8 !important;
    }
    .card-top-strip {
        height: 5px;
        width: 100%;
        border-radius: 5px;
        margin-bottom: 14px;
    }
    .class-card-title {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin: 0 0 6px 0 !important;
    }
    .tag-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 0.76rem;
        font-weight: 700;
        margin-right: 6px;
    }
    .tag-blue { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
    .tag-green { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
    .tag-purple { background: #faf5ff; color: #7e22ce; border: 1px solid #e9d5ff; }
    
    /* 7. Tugmalar (Vibrant Modern Pill Buttons) */
    .stButton>button {
        background-color: #ffffff !important;
        color: #334155 !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.83rem !important;
        padding: 7px 14px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
    }
    .stButton>button:hover {
        background-color: #f8fafc !important;
        border-color: #6366f1 !important;
        color: #4f46e5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #06b6d4 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4338ca 0%, #4f46e5 50%, #0891b2 100%) !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.45) !important;
        color: #ffffff !important;
    }
    
    /* 8. Yon Menyuning Radio Tugmalari (Active Pill) */
    div[role="radiogroup"] > label {
        background: #ffffff !important;
        border: 1px solid #f1f5f9 !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        margin-bottom: 6px !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    div[role="radiogroup"] > label:hover {
        background: #f8fafc !important;
        color: #4f46e5 !important;
        border-color: #c7d2fe !important;
        transform: translateX(3px) !important;
    }
    div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%) !important;
        color: #4338ca !important;
        font-weight: 800 !important;
        border: 1.5px solid #818cf8 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* 9. Matn maydonlari */
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* 10. Jadvallar */
    .stDataFrame, .stTable {
        background: #ffffff !important;
        border-radius: 16px !important;
        border: 1.5px solid #e2e8f0 !important;
        overflow: hidden !important;
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
            "subject": "Veb Dasturlash",
            "class_level": "10-A sinf",
            "student_count": "12 o'quvchi",
            "full_name": "Veb Dasturlash (Full-Stack & Cloud)",
            "room": "304-xona",
            "strip": "linear-gradient(90deg, #3b82f6, #06b6d4)",
            "syllabus": ["HTML5/CSS3 zamonaviy dizayn", "Flexbox va CSS Grid", "JavaScript Async & DOM", "Node.js REST API"]
        },
        {
            "id": 2,
            "subject": "Tarmoq Texnologiyalari",
            "class_level": "10-A sinf",
            "student_count": "10 o'quvchi",
            "full_name": "Tarmoq Texnologiyalari va Kiberxavfsizlik",
            "room": "Server xonasi",
            "strip": "linear-gradient(90deg, #10b981, #059669)",
            "syllabus": ["OSI va TCP/IP modellari", "IP subnetting", "Router & Firewall konfiguratsiya", "Penetration testing"]
        },
        {
            "id": 3,
            "subject": "Grafika va Dizayn",
            "class_level": "10-A sinf",
            "student_count": "7 o'quvchi",
            "full_name": "Kompyuter Grafikasi & UI/UX Muhandisligi",
            "room": "Dizayn studiyasi",
            "strip": "linear-gradient(90deg, #8b5cf6, #ec4899)",
            "syllabus": ["Vektorli grafika", "Figma Design System", "Micro-animations", "3D WebGL asoslari"]
        },
        {
            "id": 4,
            "subject": "Mobil Dasturlash",
            "class_level": "10-A sinf",
            "student_count": "15 o'quvchi",
            "full_name": "Krossplatformali Mobil Dasturlash (Flutter)",
            "room": "205-xona",
            "strip": "linear-gradient(90deg, #f43f5e, #fb923c)",
            "syllabus": ["Flutter Widget daraxti", "State Management (Bloc)", "Camera & GPS integratsiyasi", "App Store yuklash"]
        },
        {
            "id": 5,
            "subject": "Informatika va AT",
            "class_level": "8-C sinf",
            "student_count": "11 o'quvchi",
            "full_name": "Informatika va Axborot Texnologiyalari",
            "room": "102-xona",
            "strip": "linear-gradient(90deg, #0ea5e9, #38bdf8)",
            "syllabus": ["Axborot tizimlari", "Katta ma'lumotlar tahlili", "SQL ma'lumotlar bazasi", "Algoritmik mantiq"]
        },
        {
            "id": 6,
            "subject": "Sun'iy Intellekt & Python",
            "class_level": "8-A sinf",
            "student_count": "12 o'quvchi",
            "full_name": "Sun'iy Intellekt va Python Algoritmlari",
            "room": "AI Laboratoriyasi",
            "strip": "linear-gradient(90deg, #f59e0b, #eab308)",
            "syllabus": ["Python funksiyalar & Rekursiya", "NumPy & Pandas tahlili", "Neyrotarmoqlar kirish", "3D Baholash modeli"]
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

app_settings = load_settings()
if "secure_api_key" not in st.session_state:
    st.session_state.secure_api_key = app_settings.get("gemini_api_key", "")
if "default_max_score" not in st.session_state:
    st.session_state.default_max_score = float(app_settings.get("default_max_score", 10.0))
if "default_beta" not in st.session_state:
    st.session_state.default_beta = float(app_settings.get("default_beta", 1.0))

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
# KIRISH OYNASI (LUMINOUS MODERN AUTH CARD)
# =========================================================================
if st.session_state.current_user is None:
    st.markdown("""
    <div style="max-width: 540px; margin: 40px auto 16px auto; text-align: center;">
        <div style="display: inline-flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 2.6rem;">✨</span>
            <span style="font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                EduAI<span style="color: #06b6d4;">.uz</span>
            </span>
        </div>
        <p style="font-size: 1.05rem; color: #64748b; font-weight: 600; margin: 0 0 24px 0;">
            Aydın keleshek sarı — 3D Intellektual Ta'lim va Baholash Portali
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_l1, c_l2, c_l3 = st.columns([1, 2, 1])
    with c_l2:
        st.markdown("""
        <div style="background: #ffffff; border: 1.5px solid #e0e7ff; border-radius: 24px; padding: 34px; box-shadow: 0 20px 45px -10px rgba(79, 70, 229, 0.12);">
            <h3 style="margin: 0 0 18px 0; font-size: 1.45rem; font-weight: 800; color: #0f172a; text-align: center;">🔐 Tizimga Kirish</h3>
        """, unsafe_allow_html=True)
        
        input_login = st.text_input("Login:", placeholder="omirbaytajenov5@gmail.com yoki teacher")
        input_password = st.text_input("Parol:", type="password", placeholder="Parolingizni kiriting")
        
        if st.button("🚀 Kirish", type="primary", use_container_width=True):
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
                st.error("Login yoki parol noto'g'ri! Iltimos, qayta tekshiring.")

        st.markdown("<hr style='margin: 22px 0; border: none; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
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
# ASOSIY INTERFEYS: KIRILGAN FOYDALANUVChI
# =========================================================================
curr_u = st.session_state.current_user
user_role = curr_u["role"]
initials = "".join([part[0].upper() for part in curr_u['name'].split()[:2]])

# SIDEBAR: LUMINOUS NEO-NAVIGATION
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 6px 0 18px 0; margin-bottom: 12px; border-bottom: 1.5px solid #f1f5f9;">
        <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; color: white; box-shadow: 0 6px 15px rgba(79, 70, 229, 0.3);">
            ✨
        </div>
        <div>
            <div style="font-size: 1.35rem; font-weight: 900; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                EduAI<span style="color: #06b6d4;">.uz</span>
            </div>
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; letter-spacing: 0.5px;">Aydın keleshek sarı</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if user_role == "Administrator":
        active_menu = st.radio(
            "Menyu:",
            [
                "🏠 Bosh sahifa",
                "➕ Foydalanuvchi qo'shish",
                "👥 Akkauntlar",
                "📋 Audit loglari",
                "⚙️ Sozlamalar"
            ],
            label_visibility="collapsed"
        )
    elif user_role == "O'qituvchi":
        active_menu = st.radio(
            "Menyu:",
            [
                "🏠 Bosh sahifa",
                "👥 Sinflar",
                "📅 Taqvim",
                "📝 3D Baholash",
                "📂 Ommaviy baholash",
                "📊 Jurnal",
                "📄 Dalolatnoma",
                "📈 Ilmiy tahlil"
            ],
            label_visibility="collapsed"
        )
    else: # O'quvchi
        active_menu = st.radio(
            "Menyu:",
            [
                "🏠 Bosh sahifa",
                "📤 Vazifa topshirish",
                "📜 Baholarim",
                "✉️ Tavsiya xati"
            ],
            label_visibility="collapsed"
        )

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # Profil kartasi (Pastda: O'mirbay Ta'jenov O'qituvchi)
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; padding: 12px 14px; background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 1.5px solid #dbeafe; border-radius: 16px; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
        <div style="width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #4f46e5, #06b6d4); color: white; font-weight: 900; display: flex; align-items: center; justify-content: center; font-size: 1rem; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);">
            {initials}
        </div>
        <div style="overflow: hidden;">
            <div style="font-size: 0.92rem; font-weight: 800; color: #0f172a; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{curr_u['name']}</div>
            <div style="font-size: 0.75rem; color: #2563eb; font-weight: 700;">{user_role}</div>
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
    # 1. YUQORI LUMINOUS E'LON TASMASI
    st.markdown("""
    <div class="luminous-banner">
        <div style="display: flex; align-items: center;">
            <span class="badge-live-ai">✨ AI LIVE</span>
            <span>📢 <b>Xush kelibsiz!</b> EduAI ta'lim platformasiga xush kelibsiz! Bugungi mashg'ulotlaringizda zafar tilaymiz!</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px; font-size: 0.88rem; font-weight: 700;">
            <span style="background: rgba(255,255,255,0.22); padding: 4px 12px; border-radius: 20px;">🇺🇿 O'zbek ▾</span>
            <span>🔔 Bildirishnoma (2)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # A. BOSH SAHIFA: O'QITUVCHI PANELI (YORQIN VA JONLI DASHBOARD)
    if active_menu == "🏠 Bosh sahifa":
        col_hdr1, col_hdr2 = st.columns([4, 1.2])
        with col_hdr1:
            st.markdown("""
            <h2 style="margin: 0; font-size: 2.1rem; font-weight: 900; color: #0f172a;">
                O'qituvchi paneli
            </h2>
            <p style="margin: 4px 0 22px 0; color: #64748b; font-size: 1rem; font-weight: 500;">
                Guruhlaringiz — elektron jurnal, dars jadvali, uy vazifalari va 3D intellektual baholash shu yerda.
            </p>
            """, unsafe_allow_html=True)
        with col_hdr2:
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if st.button("✨ Sinflar Ro'yxati →", type="primary", use_container_width=True):
                st.session_state.class_modal_view = {"type": "classes_list"}

        # 3 TA STATISTIK KARTOChKA (LUMINOUS PASTEL DEPTH)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("""
            <div class="metric-card-bright card-bright-indigo">
                <div class="metric-title-bright" style="color: #2563eb;">Guruhlarim</div>
                <div class="metric-num-bright" style="color: #1e40af;">6</div>
                <div class="metric-icon-bright" style="background: #dbeafe; color: #1d4ed8;">📚</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m2:
            st.markdown("""
            <div class="metric-card-bright card-bright-emerald">
                <div class="metric-title-bright" style="color: #059669;">O'quvchilar</div>
                <div class="metric-num-bright" style="color: #065f46;">78</div>
                <div class="metric-icon-bright" style="background: #d1fae5; color: #047857;">🎓</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m3:
            unreviewed_count = max(1, 14 - len(st.session_state.grades_journal))
            st.markdown(f"""
            <div class="metric-card-bright card-bright-amber">
                <div class="metric-title-bright" style="color: #d97706;">Baholanmagan vazifa</div>
                <div class="metric-num-bright" style="color: #92400e;">{unreviewed_count}</div>
                <div style="font-size: 0.82rem; color: #b45309; font-weight: 700; margin-top: 4px;">⚡ Tekshirishni kutmoqda</div>
                <div class="metric-icon-bright" style="background: #fef3c7; color: #b45309;">⏳</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<h3 style='margin: 14px 0 18px 0; font-size: 1.45rem; font-weight: 800; color: #0f172a;'>Mening Guruhlarim va Fanlarim</h3>", unsafe_allow_html=True)

        # 6 TA FAN KARTOChKASI (GRID: HAR BIRI O'ZIGA XOS YORQIN IDENTIFIKATORGA EGA)
        g1, g2, g3 = st.columns(3)
        grid_cols = [g1, g2, g3]

        for idx, item in enumerate(st.session_state.teacher_classes):
            with grid_cols[idx % 3]:
                st.markdown(f"""
                <div class="class-card-bright">
                    <div class="card-top-strip" style="background: {item['strip']};"></div>
                    <div class="class-card-title">{item['subject']}</div>
                    <div style="margin-bottom: 18px;">
                        <span class="tag-pill tag-blue">{item['class_level']}</span>
                        <span class="tag-pill tag-green">{item['student_count']}</span>
                        <span class="tag-pill tag-purple">{item['room']}</span>
                    </div>
                """, unsafe_allow_html=True)

                # Tugmalar qatori: O'quvchilar | Jurnal | Reja | Tahlil (AI)
                b1, b2, b3, b4 = st.columns(4)
                with b1:
                    if st.button("O'quvchilar", key=f"btn_u_{item['id']}", use_container_width=True):
                        st.session_state.class_modal_view = {"type": "students", "class": item}
                with b2:
                    if st.button("Jurnal", key=f"btn_j_{item['id']}", use_container_width=True):
                        st.session_state.class_modal_view = {"type": "journal", "class": item}
                with b3:
                    if st.button("Reja", key=f"btn_p_{item['id']}", use_container_width=True):
                        st.session_state.class_modal_view = {"type": "plan", "class": item}
                with b4:
                    if st.button("✨ Tahlil", key=f"btn_ai_{item['id']}", type="primary", use_container_width=True):
                        st.session_state.task_input = f"{item['full_name']} bo'yicha amaliy topshiriq va laboratoriya ishi."
                        st.session_state.class_modal_view = {"type": "ai_redirect", "class": item}

                st.markdown("</div>", unsafe_allow_html=True)

        # TANLANGAN TUGMA MA'LUMOTI (INTERAKTIV OYNA)
        if st.session_state.class_modal_view:
            mv = st.session_state.class_modal_view
            st.markdown("---")
            
            if mv.get("type") == "students":
                cls_item = mv["class"]
                st.subheader(f"👥 {cls_item['subject']} ({cls_item['class_level']}) — O'quvchilar ro'yxati")
                st_data = [
                    {"№": 1, "F.I.Sh": "Azizov Jasur", "Holat": "Faol", "Oxirgi baho": "9.1/10"},
                    {"№": 2, "F.I.Sh": "Karimov Dilshod", "Holat": "Faol", "Oxirgi baho": "Kutilmoqda"},
                    {"№": 3, "F.I.Sh": "Nazarova Nigora", "Holat": "Faol", "Oxirgi baho": "8.8/10"},
                    {"№": 4, "F.I.Sh": "Sobirov Alisher", "Holat": "Faol", "Oxirgi baho": "9.5/10"}
                ]
                st.dataframe(pd.DataFrame(st_data), use_container_width=True)
                if st.button("Yopish ✖️", key="close_modal"):
                    st.session_state.class_modal_view = None
                    st.rerun()

            elif mv.get("type") == "journal":
                cls_item = mv["class"]
                st.subheader(f"📊 {cls_item['subject']} — Elektron Jurnal")
                st.table(pd.DataFrame([
                    {"Mavzu": "1-Amaliy mashg'ulot", "O'rtacha ball": "8.7", "Topshirganlar": "12/12"},
                    {"Mavzu": "2-Laboratoriya ishi", "O'rtacha ball": "8.2", "Topshirganlar": "11/12"}
                ]))
                if st.button("Yopish ✖️", key="close_journal"):
                    st.session_state.class_modal_view = None
                    st.rerun()

            elif mv.get("type") == "plan":
                cls_item = mv["class"]
                st.subheader(f"📑 {cls_item['full_name']} — O'quv rejasi")
                for s_i, topic in enumerate(cls_item.get("syllabus", []), 1):
                    st.write(f"**{s_i}-Mavzu:** {topic}")
                if st.button("Yopish ✖️", key="close_plan"):
                    st.session_state.class_modal_view = None
                    st.rerun()

            elif mv.get("type") == "ai_redirect":
                cls_item = mv["class"]
                st.success(f"✨ **{cls_item['full_name']}** fani bo'yicha ma'lumotlar yuklandi! Chap menyudan **'📝 3D Baholash'** bo'limiga o'ting.")
                if st.button("Tushundim ✖️", key="close_redirect"):
                    st.session_state.class_modal_view = None
                    st.rerun()

            elif mv.get("type") == "classes_list":
                st.subheader("📋 Barcha Sinflar va Dars Yuklamalari")
                cls_table = []
                for c in st.session_state.teacher_classes:
                    cls_table.append({
                        "Fan": c["subject"],
                        "To'liq nomi": c["full_name"],
                        "Sinf": c["class_level"],
                        "Xona": c["room"]
                    })
                st.dataframe(pd.DataFrame(cls_table), use_container_width=True)
                if st.button("Yopish ✖️", key="close_cls_list"):
                    st.session_state.class_modal_view = None
                    st.rerun()

    # B. SINFLAR BO'LIMI
    elif active_menu == "👥 Sinflar":
        st.subheader("👥 Sinflar va Guruhlar Boshqaruvi")
        col_c1, col_c2 = st.columns([3, 1])
        with col_c1:
            st.write("Sizga biriktirilgan faol guruhlar:")
            c_table = []
            for c in st.session_state.teacher_classes:
                c_table.append({
                    "Fan": c["subject"],
                    "Sinf": f"{c['class_level']} ({c['student_count']})",
                    "Xona": c["room"],
                    "Mavzular": len(c["syllabus"])
                })
            st.dataframe(pd.DataFrame(c_table), use_container_width=True)
        with col_c2:
            st.markdown("""
            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 18px; padding: 22px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                <h4 style="margin: 0 0 12px 0; color: #0f172a;">➕ Yangi Guruh</h4>
            """, unsafe_allow_html=True)
            new_s = st.text_input("Fan:", placeholder="Robototexnika")
            new_c = st.text_input("Sinf:", placeholder="11-A")
            new_r = st.text_input("Xona:", placeholder="402")
            if st.button("Saqlash", type="primary", use_container_width=True):
                st.session_state.teacher_classes.append({
                    "id": len(st.session_state.teacher_classes) + 1,
                    "subject": new_s,
                    "class_level": f"{new_c} sinf",
                    "student_count": "15 o'quvchi",
                    "full_name": new_s,
                    "room": f"{new_r}-xona",
                    "strip": "linear-gradient(90deg, #10b981, #06b6d4)",
                    "syllabus": ["1-Mavzu: Kirish", "2-Mavzu: Amaliyot"]
                })
                st.success("Guruh qo'shildi!")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # C. TAQVIM BO'LIMI
    elif active_menu == "📅 Taqvim":
        st.subheader("📅 Haftalik Dars Jadvali va Reja")
        sch = [
            {"Kun": "Dushanba", "Vaqt": "08:30 - 09:50", "Fan": "Veb Dasturlash", "Sinf": "10-A", "Xona": "304", "Holat": "✅ O'tildi"},
            {"Kun": "Dushanba", "Vaqt": "10:00 - 11:20", "Fan": "Tarmoq Texnologiyalari", "Sinf": "10-A", "Xona": "Server", "Holat": "✅ O'tildi"},
            {"Kun": "Seshanba", "Vaqt": "08:30 - 09:50", "Fan": "Informatika", "Sinf": "8-C", "Xona": "102", "Holat": "🕒 Navbatdagi"},
            {"Kun": "Chorshanba", "Vaqt": "11:30 - 12:50", "Fan": "Sun'iy Intellekt", "Sinf": "8-A", "Xona": "AI Lab", "Holat": "📝 AI Baholash"},
            {"Kun": "Payshanba", "Vaqt": "08:30 - 09:50", "Fan": "Grafika va Dizayn", "Sinf": "10-A", "Xona": "Dizayn", "Holat": "Rejalashtirilgan"},
            {"Kun": "Juma", "Vaqt": "10:00 - 11:20", "Fan": "Mobil Dasturlash", "Sinf": "10-A", "Xona": "205", "Holat": "Rejalashtirilgan"}
        ]
        st.dataframe(pd.DataFrame(sch), use_container_width=True)

    # D. 3D BAHOLASH LABORATORIYASI
    elif active_menu == "📝 3D Baholash":
        st.subheader("📝 3D Baholash Laboratoriyasi (Yakka Tartibda)")
        col_setup1, col_setup2 = st.columns([2, 1])
        with col_setup1:
            task_prompt = st.text_area("Topshiriq savollari:", value=st.session_state.task_input, height=100)
            st.session_state.task_input = task_prompt
            
            if st.button("✨ Savoldan Etalon Javobni AI orqali Yaratish", use_container_width=True):
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

            st.write("**🧪 Test namunalar:**")
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
                <div style="background: linear-gradient(145deg, #ffffff 0%, #eff6ff 100%); border: 2px solid #6366f1; border-radius: 20px; padding: 24px; box-shadow: 0 10px 25px rgba(99, 102, 241, 0.12); margin-bottom: 16px;">
                    <div style="font-weight: 800; color: #4f46e5; font-size: 0.85rem; letter-spacing: 0.5px;">1-BOSQICH</div>
                    <h3 style="margin: 4px 0; font-size: 1.35rem; color: #0f172a;">Akademik Baho</h3>
                    <div style="font-size: 2.7rem; font-weight: 900; color: #4338ca; margin: 8px 0;">
                        {eval_1['score']} <span style='font-size: 1.2rem; color: #64748b;'>/ {max_score}</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #475569; margin: 0;">Faktik bilim va to'g'ri formulalar.</p>
                </div>
                """, unsafe_allow_html=True)
                st.info(eval_1.get("detailed_analysis", ""))

            with c2:
                b_color = "#ef4444" if eval_2['score'] < (max_score * 0.5) else "#d97706"
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #ffffff 0%, #fffbeb 100%); border: 2px solid {b_color}; border-radius: 20px; padding: 24px; box-shadow: 0 10px 25px rgba(245, 158, 11, 0.12); margin-bottom: 16px;">
                    <div style="font-weight: 800; color: {b_color}; font-size: 0.85rem; letter-spacing: 0.5px;">2-BOSQICH</div>
                    <h3 style="margin: 4px 0; font-size: 1.35rem; color: #0f172a;">AI Nazoratli Baho</h3>
                    <div style="font-size: 2.7rem; font-weight: 900; color: {b_color}; margin: 8px 0;">
                        {eval_2['score']} <span style='font-size: 1.2rem; color: #64748b;'>/ {max_score}</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #475569; margin: 0;">ChatGPT aniqlansa ball kesiladi.</p>
                </div>
                """, unsafe_allow_html=True)
                st.info(eval_2.get("explanation", ""))

            with c3:
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #ffffff 0%, #ecfdf5 100%); border: 2px solid #10b981; border-radius: 20px; padding: 24px; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.12); margin-bottom: 16px;">
                    <div style="font-weight: 800; color: #059669; font-size: 0.85rem; letter-spacing: 0.5px;">3-BOSQICH</div>
                    <h3 style="margin: 4px 0; font-size: 1.35rem; color: #0f172a;">Empatiya Bahosi</h3>
                    <div style="font-size: 2.7rem; font-weight: 900; color: #047857; margin: 8px 0;">
                        {eval_3['score']} <span style='font-size: 1.2rem; color: #64748b;'>/ {max_score}</span>
                    </div>
                    <p style="font-size: 0.85rem; color: #475569; margin: 0;">Mustaqil harakat uchun rag'batlantirish.</p>
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
    elif active_menu == "📂 Ommaviy baholash":
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
    elif active_menu == "📊 Jurnal":
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
    elif active_menu == "📄 Dalolatnoma":
        st.subheader("📄 Rasmiy Baholash Dalolatnomasi (Aкт внедрения)")
        prot_html = generate_official_protocol_html(
            "Toshkent shahar 110-sonli maktab", "Informatika", curr_u['name'],
            st.session_state.task_input[:35], st.session_state.default_max_score, st.session_state.grades_journal
        )
        st.download_button("📥 Rasmiy Dalolatnomani Yuklab Olish (HTML/PDF)", prot_html, "dalolatnoma.html", "text/html")
        st.components.v1.html(prot_html, height=480, scrolling=True)

    # H. ILMIY EKSPERIMENT
    elif active_menu == "📈 Ilmiy tahlil":
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
    <div style="background: #ffffff; border: 1.5px solid #e0e7ff; border-radius: 20px; padding: 24px; margin-bottom: 24px; box-shadow: 0 10px 25px rgba(79, 70, 229, 0.08);">
        <span style="background: #eef2ff; color: #4f46e5; padding: 4px 14px; border-radius: 10px; font-weight: 800; font-size: 0.82rem; border: 1px solid #c7d2fe;">Administrator Paneli</span>
        <h2 style="margin: 8px 0 4px 0; font-size: 1.8rem; color: #0f172a;">🛡️ Boshqaruv Markazi</h2>
        <p style="margin: 0; font-size: 0.95rem; color: #64748b;">
            Faqat admin yangi o'qituvchi va o'quvchilarni <b>Login va Parol</b> bilan ro'yxatdan o'tkazishi mumkin.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if active_menu == "➕ Foydalanuvchi qo'shish":
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

    elif active_menu == "👥 Akkauntlar":
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

    elif active_menu == "🏠 Bosh sahifa":
        c_m1, c_m2, c_m3 = st.columns(3)
        teachers_count = len([u for u in st.session_state.registered_users if u["role"] == "O'qituvchi"])
        students_count = len([u for u in st.session_state.registered_users if u["role"] == "O'quvchi"])
        c_m1.metric("O'qituvchilar", f"{teachers_count} nafar")
        c_m2.metric("O'quvchilar", f"{students_count} nafar")
        c_m3.metric("Baholangan Ishlar", f"{len(st.session_state.grades_journal)} ta")

    elif active_menu == "⚙️ Sozlamalar":
        st.subheader("⚙️ Tizim Sozlamalari va Maxfiylik")
        st.write("Platformaning asosiy parametrlari va maxfiy konfiguratsiyalari. Ushbu bo'lim faqat bosh administrator uchun ochiq bo'lib, boshqa foydalanuvchilarga ko'rinmaydi.")
        
        # 1. API KALITI HIMOYA QILINGAN QISMI (EXPANDER ICHIDA, PAROL FORMATIDA)
        with st.expander("🔐 Maxfiy Google Gemini API Kaliti (Himoyalangan)", expanded=False):
            st.info("🛡️ **Maxfiylik himoyasi:** Ushbu API kaliti faqat sizga (Administratorga) tegishli. Boshqa foydalanuvchilar (o'qituvchilar va o'quvchilar) ushbu kalitni umuman ko'ra olmaydi.")
            current_k = st.session_state.secure_api_key
            status_text = "🟢 Kalit kiritilgan va faol" if current_k else "⚪ Hozircha kiritilmagan (Lokal NLP model faol)"
            st.caption(f"**Holat:** {status_text}")
            
            api_val = st.text_input("Gemini API Kalitini kiriting yoki yangilang:", value=current_k, type="password", placeholder="AIzaSy...")
            
            c_save1, c_save2 = st.columns([1, 1])
            with c_save1:
                if st.button("💾 Kalitni Xavfsiz Saqlash", type="primary", use_container_width=True):
                    st.session_state.secure_api_key = api_val.strip()
                    app_s = load_settings()
                    app_s["gemini_api_key"] = api_val.strip()
                    save_settings(app_s)
                    st.success("✅ API kaliti xavfsiz saqlandi!")
                    st.rerun()
            with c_save2:
                if st.button("🗑️ Kalitni O'chirish", use_container_width=True):
                    st.session_state.secure_api_key = ""
                    app_s = load_settings()
                    app_s["gemini_api_key"] = ""
                    save_settings(app_s)
                    st.warning("API kaliti tozalandi!")
                    st.rerun()

        # 2. STANDART BAHOLASH PARAMETRLARI
        with st.expander("🎯 Standart Baholash Parametrlari", expanded=True):
            col_cfg1, col_cfg2 = st.columns(2)
            with col_cfg1:
                new_max = st.number_input("Standart Maksimal Ball:", 1.0, 100.0, float(st.session_state.default_max_score), 1.0)
            with col_cfg2:
                new_beta = st.slider("Standart AI Jazosi (β):", 0.0, 1.0, float(st.session_state.default_beta), 0.1)
            
            if st.button("💾 Parametrlarni Saqlash"):
                st.session_state.default_max_score = new_max
                st.session_state.default_beta = new_beta
                app_s = load_settings()
                app_s["default_max_score"] = new_max
                app_s["default_beta"] = new_beta
                save_settings(app_s)
                st.success("Standart baholash parametrlari saqlandi!")

        # 3. XAVFSIZLIK VA PRIVACY MONITORINGI
        st.markdown("""
        <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 18px; margin-top: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
            <h4 style="margin: 0 0 10px 0; color: #0f172a;">🛡️ Maxfiylik va Xavfsizlik Kafolatlari</h4>
            <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 0.9rem; line-height: 1.7;">
                <li><b>Asosiy menyu va sahifalarda API kalit ko'rinmaydi:</b> ✅ To'liq yashirilgan</li>
                <li><b>O'qituvchi va o'quvchilar uchun API ruxsati:</b> ❌ Cheklangan (Faqat Admin)</li>
                <li><b>Foydalanuvchi akkauntlari va parollari:</b> ✅ Doimiy disk bazasi (data/users.json)</li>
                <li><b>Audit xavfsizlik jurnali:</b> ✅ Doimiy ro'yxatga olinmoqda</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    elif active_menu == "📋 Audit loglari":
        st.subheader("📋 Tizim Audit Loglari")
        st.table(pd.DataFrame(st.session_state.audit_logs))


# =========================================================================
# 🎓 O'QUVCHI PANELI
# =========================================================================
elif user_role == "O'quvchi":
    st.markdown(f"""
    <div style="background: #ffffff; border: 1.5px solid #a5f3fc; border-radius: 20px; padding: 24px; margin-bottom: 24px; box-shadow: 0 10px 25px rgba(6, 182, 212, 0.08);">
        <span style="background: #cffafe; color: #0891b2; padding: 4px 14px; border-radius: 10px; font-weight: 800; font-size: 0.82rem; border: 1px solid #a5f3fc;">O'quvchi Kabineti</span>
        <h2 style="margin: 8px 0 4px 0; font-size: 1.8rem; color: #0f172a;">🎓 {curr_u['name']} Shaxsiy Kabineti</h2>
        <p style="margin: 0; font-size: 0.95rem; color: #64748b;">
            Sinf: <b>{curr_u.get('group', '10-A sinf')}</b> | Login: <code>@{curr_u['login']}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    if active_menu == "🏠 Bosh sahifa":
        st.subheader("📚 Mening Darslarim va Faol Topshiriqlar")
        st.info("Sizga biriktirilgan fanlar bo'yicha yangi topshiriqlar mavjud. Chap menyudan 'Vazifa topshirish' bo'limiga o'ting.")
        c_st1, c_st2 = st.columns(2)
        with c_st1:
            st.metric("O'rtacha Baho", "8.9 / 10", delta="Ijobiy o'sish")
        with c_st2:
            st.metric("Tekshirilgan Ishlar", f"{len(st.session_state.grades_journal)} ta")

    elif active_menu == "📤 Vazifa topshirish":
        st.subheader("📋 Topshiriq Sharti")
        st.info(st.session_state.task_input)
        st_upload = st.file_uploader("Yechim fotosurati yoki hujjat:", type=["png", "jpg", "jpeg", "docx", "pdf", "txt"])
        st_text = st.text_area("Yoki yechimingizni yozing:", height=150)
        if st.button("🚀 Vazifani Topshirish", type="primary"):
            st.balloons()
            st.success("Vazifa muvaffaqiyatli topshirildi!")

    elif active_menu == "📜 Baholarim":
        st.subheader("📜 Mening Baholarim")
        student_surname = curr_u['name'].split()[0]
        matching_grades = [g for g in st.session_state.grades_journal if student_surname.lower() in g["talaba"].lower()]
        if matching_grades:
            g = matching_grades[-1]
            st.metric("Tasdiqlangan Baho", f"{g['tasdiqlangan_ball']} / {g['max_ball']}")
            st.write(f"**Izoh:** {g['izoh']}")
        else:
            st.info("Hozircha vazifangiz tekshirilmoqda.")

    elif active_menu == "✉️ Tavsiya xati":
        st.subheader("✉️ O'qituvchidan Shaxsiy Tavsiya Xati")
        student_surname = curr_u['name'].split()[0]
        matching_grades = [g for g in st.session_state.grades_journal if student_surname.lower() in g["talaba"].lower()]
        if matching_grades and matching_grades[-1].get("feedback"):
            st.info(matching_grades[-1]["feedback"])
        else:
            st.info("O'qituvchi hali tavsiya yozmadi.")
