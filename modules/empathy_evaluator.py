"""
3-BAHOLASH MODULI: Pedagogik Empatiya va Harakat Bahosi (Empathy & Effort-Based Grading)
"O'qituvchi o'rniga o'zini qo'yib ko'rish" konsepsiyasi:
Agar o'quvchi xato qilgan bo'lsa ham, mustaqil harakat qilgani, izlangani,
oraliq qadamlarni yozgani va daftarda ter to'kkani uchun insoniy, rag'batlantiruvchi
mustaqil 3-umumiy baho qo'yiladi.
"""

import re
from typing import Dict, List, Any

EFFORT_INDICATORS = [
    r'\bmenimcha\b',
    r'\bmen shunday o[\'’`]?ylayman\b',
    r'\bfikrimcha\b',
    r'\burinib ko[\'’`]?rdim\b',
    r'\bhisoblab chiqdim\b',
    r'\bmenda shunday chiqdi\b',
    r'\bbu yerda xato bo[\'’`]?lishi mumkin\b',
    r'\bbirinchi navbatda\b',
    r'\bdastlab\b',
    r'\bchunki\b'
]

class EmpathyEvaluator:
    def __init__(self):
        pass

    def evaluate_with_empathy(
        self,
        student_answer: str,
        base_academic_score: float,
        max_score: float = 100.0,
        is_handwritten_or_image: bool = False
    ) -> Dict[str, Any]:
        """
        3-Yondashuv: O'qituvchi empatiyasi va harakatni inobatga olgan to'liq mustaqil baho.
        """
        clean_text = student_answer.strip()
        if not clean_text or len(clean_text) < 10:
            return {
                "score": 0.0,
                "max_score": max_score,
                "grit_level": "Harakat sezilmadi",
                "empathy_notes": ["O'quvchi tomonidan mustaqil urinish qayd etilmadi."],
                "explanation": "Topshiriq bo'sh, rag'batlantirish uchun asos yo'q."
            }

        effort_points = 0.0
        empathy_notes = []

        # 1. Daftarga qo'lda yozilganlik (jismoniy mehnat bonusi)
        if is_handwritten_or_image:
            effort_points += 0.30
            empathy_notes.append("Vazifa qo'lda daftarga bajarilgan — o'quvchi shaxsan ter to'kkan.")

        # 2. Mustaqil fikr va samimiy urinish
        lower_text = clean_text.lower()
        personal_attempts = [ind for ind in EFFORT_INDICATORS if re.search(ind, lower_text)]
        if personal_attempts:
            effort_points += min(0.35, len(personal_attempts) * 0.12)
            empathy_notes.append("O'z so'zlari va tushunchasi bilan erkin tushuntirishga uringan.")

        # 3. Yechim qadamlari va hisob-kitob urinishlari (xato bo'lsa ham)
        has_intermediate_steps = bool(re.search(r'(\d+[\+\-\*\/=]\d+|qadam|bosqich|natijada|shuning uchun)', lower_text))
        if has_intermediate_steps:
            effort_points += 0.25
            empathy_notes.append("Yechim yo'li, oraliq qadamlar va hisob-kitoblar ko'rsatilgan.")

        # 4. Kengroq yozishga intilish
        word_count = len(clean_text.split())
        if word_count > 35:
            effort_points += 0.15
            empathy_notes.append("Dangasalik qilmasdan masalani tushuntirishga vaqt ajratgan.")

        effort_ratio = min(1.0, effort_points)

        # 3-Baholash: O'qituvchi empatiyasi bilan yakuniy bahoni hisoblash
        # Agar talaba urinib ko'rgan bo'lsa, xatolariga qaramay pedagogik rag'bat beriladi
        encouragement_value = effort_ratio * (max_score * 0.30)
        empathetic_score = base_academic_score + encouragement_value
        
        # Max ball doirasida chegaralash
        score_3 = round(min(max_score, max(base_academic_score, empathetic_score)), 1)

        if effort_ratio >= 0.60:
            grit_level = "Yuqori (Faol izlanuvchi o'quvchi)"
            explanation = (
                f"O'qituvchi empatiyasi: O'quvchi xato qilgan bo'lsa ham, mustaqil uringani va "
                f"fikrlash qadamlari uchun rag'batlantirildi. Baho {score_3}/{max_score} ga oshirildi."
            )
        elif effort_ratio >= 0.30:
            grit_level = "O'rtacha (Yaxshi harakat)"
            explanation = (
                f"O'qituvchi empatiyasi: Mustaqil harakat va qadamlar hisobga olindi. "
                f"Baho: {score_3}/{max_score}."
            )
        else:
            grit_level = "Past (Kam urinish)"
            explanation = (
                f"O'quvchi minimal harakat qilgan, shuning uchun baho o'zgarishsiz qoldi: {score_3}/{max_score}."
            )

        return {
            "score": score_3,
            "max_score": max_score,
            "grit_level": grit_level,
            "effort_ratio": round(effort_ratio, 2),
            "empathy_notes": empathy_notes,
            "explanation": explanation
        }
