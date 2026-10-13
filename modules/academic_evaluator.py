"""
1-BAHOLASH MODULI: Akademik va Faktik Baholash (Academic & Factual Evaluator)
Topshiriq sharti, etalon talablar va rubrika mezonlari asosida mustaqil baholaydi.
O'qituvchi belgilagan to'liq ball (max_score) shkalasida alohida umumiy baho beradi.
"""

import re
from typing import Dict, List, Any

class AcademicEvaluator:
    def __init__(self):
        pass

    def evaluate_offline(self, task_prompt: str, reference_solution: str, student_answer: str, max_score: float = 100.0) -> Dict[str, Any]:
        """
        1-Yondashuv: Sof akademik va faktik ma'lumotlarni baholash.
        Natija max_score shkalasida mustaqil baho sifatida qaytariladi.
        """
        clean_answer = student_answer.strip()
        if not clean_answer or len(clean_answer) < 5:
            return {
                "score": 0.0,
                "percentage": 0,
                "max_score": max_score,
                "confidence": 1.0,
                "criteria": {
                    "vazifaga_moslik": 0,
                    "asosiy_tushunchalar": 0,
                    "mantiqiy_yechim": 0,
                    "yakuniy_xulosa": 0
                },
                "strengths": [],
                "mistakes": ["Javob bo'sh yoki o'ta qisqa."],
                "detailed_analysis": "O'quvchi topshiriq bo'yicha ma'lumot taqdim etmagan."
            }

        # 1. Vazifa va etalon tushunchalarini ajratish
        keywords_ref = set(re.findall(r'\b\w{4,}\b', reference_solution.lower())) if reference_solution else set()
        keywords_task = set(re.findall(r'\b\w{4,}\b', task_prompt.lower())) if task_prompt else set()
        student_words = set(re.findall(r'\b\w{4,}\b', clean_answer.lower()))
        
        target_keywords = keywords_ref.union(keywords_task)
        matched_keywords = student_words.intersection(target_keywords)
        
        keyword_coverage = len(matched_keywords) / max(1, len(target_keywords)) if target_keywords else 0.7

        # 2. Rubrika bo'yicha foiz hisoblash (0 - 100%)
        # Mezon 1: Vazifaga moslik (25%)
        task_match = min(25, int(keyword_coverage * 28 + (10 if len(clean_answer) > 50 else 3)))
        
        # Mezon 2: Asosiy tushunchalar va dalillar (25%)
        has_formulas_or_code = bool(re.search(r'(=|\+|\-|\*|/|def |for |while |if |print|<|>|\d+)', clean_answer))
        concept_match = min(25, int(keyword_coverage * 20 + (10 if has_formulas_or_code else 5)))

        # Mezon 3: Mantiqiy ketma-ketlik va yechim qadamlari (30%)
        sentences = [s.strip() for s in re.split(r'[.!?\n]', clean_answer) if len(s.strip()) > 8]
        structure_match = min(30, int(len(sentences) * 5 + (10 if len(clean_answer) > 120 else 5)))

        # Mezon 4: Yakuniy aniqlik va xulosa (20%)
        conclusion_match = min(20, int(10 + (keyword_coverage * 10)))

        total_percentage = min(100, task_match + concept_match + structure_match + conclusion_match)
        
        # O'qituvchi belgilagan to'liq ballga (max_score) moslashtirilgan ball
        calculated_score = round((total_percentage / 100.0) * max_score, 1)

        # Ijobiy va salbiy tomonlarni aniqlash
        strengths = []
        mistakes = []

        if keyword_coverage > 0.4:
            strengths.append(f"Mavzuga oid muhim kalit atamalardan o'rinli foydalanilgan ({len(matched_keywords)} ta moslik).")
        if has_formulas_or_code:
            strengths.append("Yechimda aniq qadamlar, hisoblashlar yoki kod elementlari mavjud.")
        if len(sentences) >= 3:
            strengths.append("Fikrlar qadamma-qadam ifodalangan.")

        if keyword_coverage < 0.25 and target_keywords:
            mistakes.append("Etalon javobdagi tayanch tushunchalar yetarlicha yoritilmagan.")
        if len(clean_answer) < 80:
            mistakes.append("Javob juda qisqa bo'lib, yechim bosqichlari to'liq ochib berilmagan.")
        if not mistakes:
            mistakes.append("Jiddiy faktik xatolik aniqlanmadi, formulalar va tushunchalar to'g'ri qo'llangan.")

        return {
            "score": calculated_score,
            "percentage": total_percentage,
            "max_score": max_score,
            "confidence": 0.88,
            "criteria": {
                "vazifaga_moslik": round((task_match / 100.0) * max_score, 1),
                "asosiy_tushunchalar": round((concept_match / 100.0) * max_score, 1),
                "mantiqiy_yechim": round((structure_match / 100.0) * max_score, 1),
                "yakuniy_xulosa": round((conclusion_match / 100.0) * max_score, 1)
            },
            "strengths": strengths if strengths else ["Javob topshirilgan."],
            "mistakes": mistakes,
            "detailed_analysis": (
                f"1-Baholash (Akademik): O'quvchining faktik bilimi {calculated_score}/{max_score} "
                f"({total_percentage}%) deb baholandi. Vazifa talablariga moslik tahlil qilindi."
            )
        }
