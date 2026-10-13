"""
Fayllarni qabul qilish va matnga aylantirish moduli (Multimodal Ingestion Pipeline)
Qo'llab-quvvatlanadigan formatlar:
- DOCX (Microsoft Word)
- PDF (Acrobat Reader / hujjatlar)
- TXT (Matnli fayllar)
- Rasm (PNG, JPG, JPEG - Qo'lyozma daftar yoki skrinshotlar)
"""

import io
import re
from typing import Tuple, Optional
from PIL import Image
import docx
import pypdf

def extract_text_from_txt(file_bytes: bytes) -> str:
    """TXT fayldan matnni ajratib olish (UTF-8 va boshqa kodirovkalar)."""
    for encoding in ['utf-8', 'windows-1251', 'latin-1']:
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return file_bytes.decode('utf-8', errors='ignore').strip()

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Word (.docx) fayldan matn va jadvallarni ajratib olish."""
    doc = docx.Document(io.BytesIO(file_bytes))
    full_text = []
    
    # Paragraflarni o'qish
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())
            
    # Jadvallarni o'qish
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                full_text.append(" | ".join(row_text))
                
    return "\n\n".join(full_text)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF hujjatdan sahifama-sahifa matnni ajratib olish."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    full_text = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            full_text.append(f"--- Sahifa {idx + 1} ---\n" + text.strip())
    return "\n\n".join(full_text)

def process_image_file(file_bytes: bytes) -> Tuple[Image.Image, dict]:
    """
    Rasm faylini (PNG/JPG) qayta ishlash.
    Rasm metama'lumotlarini (o'lchami, ranglar xilma-xilligi, qo'lyozmaga xos xususiyatlar) aniqlaydi.
    """
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    width, height = image.size
    
    # Rasm xususiyatlari tahlili
    info = {
        "width": width,
        "height": height,
        "aspect_ratio": round(width / max(1, height), 2),
        "format": image.format if hasattr(image, 'format') else "JPEG",
        "has_content": width > 50 and height > 50
    }
    return image, info

def parse_uploaded_file(file_bytes: bytes, file_name: str) -> Tuple[str, Optional[Image.Image], str]:
    """
    Yuklangan fayl turini aniqlaydi va kerakli parserga yo'naltiradi.
    Qaytaradi: (ajratilgan_matn, image_ob'ekti_agar_mavjud_bo'lsa, fayl_turi)
    """
    name_lower = file_name.lower()
    
    if name_lower.endswith('.txt'):
        text = extract_text_from_txt(file_bytes)
        return text, None, "TXT Hujjati"
        
    elif name_lower.endswith('.docx'):
        text = extract_text_from_docx(file_bytes)
        return text, None, "Word (.docx) Hujjati"
        
    elif name_lower.endswith('.pdf'):
        text = extract_text_from_pdf(file_bytes)
        return text, None, "PDF Hujjati"
        
    elif any(name_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
        image, _ = process_image_file(file_bytes)
        # Rasmdan matnni multimodal AI yoki heuristika keyinroq oladi
        return "[Rasm yuklandi: Daftar sahifasi yoki yechim skrinshoti]", image, "Rasm / Qo'lyozma"
        
    else:
        # Noma'lum format bo'lsa oddiy matn sifatida urinib ko'rish
        try:
            text = extract_text_from_txt(file_bytes)
            return text, None, "Matnli fayl"
        except Exception:
            return "", None, "Noma'lum format"
