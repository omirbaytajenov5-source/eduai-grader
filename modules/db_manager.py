"""
MA'LUMOTLAR BAZASI MENEJERI (JSON Database Manager)
Foydalanuvchilar, baholar va topshiriqlarni doimiy ravishda diskda (data/*.json) saqlaydi.
Shu sababli:
1. Admin yangi o'qituvchi yoki o'quvchi qo'shganda u diskka yoziladi;
2. Yangi o'quvchi boshqa brauzer, telefon yoki kompyuterdan o'z logini va paroli bilan saytga kira oladi!
3. Server o'chib-yonsa ham foydalanuvchilar o'chib ketmaydi.
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
GRADES_FILE = os.path.join(DATA_DIR, "grades.json")
AUDIT_FILE = os.path.join(DATA_DIR, "audit.json")

INITIAL_USERS = [
    {"id": 1, "name": "Omirbay Tajenov", "role": "Administrator", "login": "omirbaytajenov5@gmail.com", "password": "Omir2001@", "email": "omirbaytajenov5@gmail.com", "group": "Boshqaruv", "status": "Faol"},
    {"id": 2, "name": "Xolmatov Abror", "role": "O'qituvchi", "login": "teacher", "password": "123", "email": "abror@eduai.uz", "group": "Informatika kafedrasi", "status": "Faol"},
    {"id": 3, "name": "Karimova Zilola", "role": "O'qituvchi", "login": "karimova", "password": "123", "email": "karimova@eduai.uz", "group": "Dasturlash kafedrasi", "status": "Faol"},
    {"id": 4, "name": "Azizov Jasur", "role": "O'quvchi", "login": "jasur", "password": "123", "email": "jasur@eduai.uz", "group": "10-A sinf", "status": "Faol"},
    {"id": 5, "name": "Saidov Sardor", "role": "O'quvchi", "login": "sardor", "password": "123", "email": "sardor@eduai.uz", "group": "10-A sinf", "status": "Faol"},
    {"id": 6, "name": "Nodirova Malika", "role": "O'quvchi", "login": "malika", "password": "123", "email": "malika@eduai.uz", "group": "10-A sinf", "status": "Faol"}
]

def init_db():
    """Ma'lumotlar papkasi va fayllarini yaratish."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(INITIAL_USERS, f, ensure_ascii=False, indent=2)
    if not os.path.exists(GRADES_FILE):
        with open(GRADES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    if not os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_users() -> List[Dict[str, Any]]:
    init_db()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return INITIAL_USERS

def save_users(users: List[Dict[str, Any]]):
    init_db()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_user(name: str, role: str, login: str, password: str, email: str = "", group: str = "") -> Tuple[bool, str]:
    users = load_users()
    login_clean = login.strip().lower()
    
    # Login takrorlanmasligini tekshirish
    if any(u["login"].lower() == login_clean for u in users):
        return False, f"'{login}' logini allaqachon mavjud! Boshqa login tanlang."
        
    new_id = max([u["id"] for u in users], default=0) + 1
    new_user = {
        "id": new_id,
        "name": name.strip(),
        "role": role,
        "login": login_clean,
        "password": password.strip(),
        "email": email.strip() if email else f"{login_clean}@eduai.uz",
        "group": group.strip() if group else "Umumiy",
        "status": "Faol"
    }
    users.append(new_user)
    save_users(users)
    return True, "Foydalanuvchi muvaffaqiyatli saqlandi!"

def authenticate_user(login: str, password: str) -> Optional[Dict[str, Any]]:
    """Foydalanuvchini login va parol orqali tekshirish."""
    users = load_users()
    login_clean = login.strip().lower()
    pwd_clean = password.strip()
    
    for u in users:
        if u["login"].lower() == login_clean and u["password"] == pwd_clean:
            return u
    return None
