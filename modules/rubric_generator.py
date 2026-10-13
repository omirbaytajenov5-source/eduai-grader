"""
ETALON JAVOB VA BAHOLASH RUBRIKASINI AVTOMATIK YARATISH MODULI (Auto-Rubric & Reference Generator)
O'qituvchi faqat savollarni kiritganda, sun'iy intellekt avtomatik ravishda:
1. To'liq etalon javobni;
2. Dastur kodi yoki formulalarini;
3. Baholash rubrikasi va mezonlarini (max_score asosida) shakllantiradi.
"""

import re
from typing import Optional

class RubricGenerator:
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or ""
        self.has_llm = bool(self.api_key.strip())
        if self.has_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
            except Exception:
                self.has_llm = False

    def generate_reference_and_rubric(self, task_prompt: str, max_score: float = 10.0) -> str:
        """
        Savollar asosida to'liq etalon javob va rubrika yaratish.
        """
        clean_task = task_prompt.strip()
        if not clean_task:
            return "Topshiriq sharti kiritilmagan."

        # Agar Gemini mavjud bo'lsa, chuqur model orqali yaratish
        if self.has_llm:
            try:
                return self._generate_with_gemini(clean_task, max_score)
            except Exception:
                return self._generate_offline(clean_task, max_score)
        else:
            return self._generate_offline(clean_task, max_score)

    def _generate_offline(self, task: str, max_score: float) -> str:
        """
        Lokal / Bepul rejimda savollarni tahlil qilib professional rubrika va etalon tuzish.
        """
        # Savoldagi kalit so'zlarni tahlil qilish
        lower_task = task.lower()
        is_code = bool(re.search(r'(python|dastur|kod|funksiya|algoritm|yozing|tuzing|def |class)', lower_task))
        is_math = bool(re.search(r'(hisoblang|yeching|formula|tenglama|integral|hosila|\+|\-|\*|/)', lower_task))

        lines = []
        lines.append(f"=== AI TOMONIDAN YARATILGAN ETALON JAVOB VA RUBRIKA (Maksimal: {max_score} ball) ===")
        lines.append("")
        lines.append("1. KUTILAYOTGAN NAZARIY ASOSLAR VA KALIT TUSHUNCHALAR:")
        
        # Savoldan jumlalarni ajratib talablar tuzish
        sentences = [s.strip() for s in re.split(r'[\n\?\.]', task) if len(s.strip()) > 5]
        for idx, s in enumerate(sentences[:4], 1):
            lines.append(f"  - {idx}-talab: '{s}' bo'yicha to'liq va ilmiy ta'rif berilishi shart.")

        lines.append("")
        if is_code:
            lines.append("2. KUTILAYOTGAN AMALIY YECHIM (KOD / ALGORITM):")
            lines.append("  - Dastur kodi sintaktik to'g'ri bo'lishi;")
            lines.append("  - Kiruvchi va chiquvchi ma'lumotlar, chegaraviy holatlar tekshirilishi;")
            lines.append("  - Algoritm samaradorligi va to'g'ri o'zgaruvchilar nomlanishi.")
            lines.append("")

        if is_math:
            lines.append("2. KUTILAYOTGAN MATEMATIK BOSQICHLAR:")
            lines.append("  - Dastlabki formulaning to'g'ri qo'llanilishi;")
            lines.append("  - Oraliq hisoblash amallari aniqligi;")
            lines.append("  - Yakuniy to'g'ri sonli natija.")
            lines.append("")

        lines.append(f"3. BAHOLASH RUBRIKASI (JAMI: {max_score} BALL):")
        p1 = round(max_score * 0.35, 1)
        p2 = round(max_score * 0.40, 1)
        p3 = round(max_score * 0.25, 1)
        lines.append(f"  - Nazariy tushunchalar va mavzuga moslik: {p1} ball")
        lines.append(f"  - Yechim qadamlari, formulalar yoki dastur kodi: {p2} ball")
        lines.append(f"  - Xulosa, to'g'ri natija va tushuntirish: {p3} ball")
        
        return "\n".join(lines)

    def _generate_with_gemini(self, task: str, max_score: float) -> str:
        """Gemini orqali mukammal darslik darajasidagi etalon va rubrika yaratish."""
        prompt = f"""
Sen malakali universitet o'qituvchisisan.
Quyidagi topshiriq savollari uchun mukammal ETALON JAVOB va BAHOLASH RUBRIKASINI ishlab chiq:

[TOPSHIRIQ SAVOLLARI]:
{task}

[UMUMIY BALL]: {max_score} ball

Tuzilishi:
1. To'liq etalon ilmiy javob (ta'riflar, zarur bo'lsa dastur kodi yoki formulalar).
2. O'quvchi javobida bo'lishi shart bo'lgan kalit atamalar.
3. Baholash rubrikasi ({max_score} ballning qismlarga taqsimoti).

O'zbek tilida aniq, tushunarli qilib yoz.
"""
        model = self.genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
