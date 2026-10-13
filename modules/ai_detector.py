"""
2-BAHOLASH MODULI: AI Nazorati va Anti-Plagiat bilan Baholash (AI-Supervised Grading)
Agar o'quvchi topshiriqni ChatGPT/LLM orqali bajargan bo'lsa, ushbu baholashda ball
kesiladi yoki holatga qarab umuman baho qo'yilmaydi (0 ball).
Mustaqil 2-umumiy baho sifatida qaytariladi.
"""

import re
import math
from typing import Dict, List, Any

AI_CLICHE_PATTERNS = [
    # O'zbekcha
    r'\bxulosa qilib aytganda\b',
    r'\bshuni ta[\'’`]?kidlash joizki\b',
    r'\bshuni unutmaslik kerakki\b',
    r'\bkeling[,\s]+ko[\'’`]?rib chiqamiz\b',
    r'\bmuhim ahamiyatga ega\b',
    r'\bmuhim rol o[\'’`]?ynaydi\b',
    r'\bshubhasiz[,\s]\b',
    r'\bxulosa o[\'’`]?rnida\b',
    r'\bbir tomondan.*ikkinchi tomondan\b',
    r'\bquyidagilardan iborat\b',
    r'\bzamonaviy dunyoda\b',
    r'\bhozirgi kunda\b',
    
    # Ruscha
    r'\bв заключение\b',
    r'\bследует отметить[,\s] что\b',
    r'\bважно подчеркнуть\b',
    r'\bтаким образом[,\s]\b',
    r'\bиграет важную роль\b',
    r'\bдавайте рассмотрим\b',
    
    # Inglizcha
    r'\bin conclusion\b',
    r'\bit is important to note\b',
    r'\bfurthermore\b',
    r'\bmoreover\b',
    r'\bplays a crucial role\b',
    r'\bdelve into\b',
    r'\btestament to\b'
]

class AIDetector:
    def __init__(self):
        pass

    def calculate_burstiness(self, sentences: List[str]) -> float:
        """Burstiness (jumlalar uzunligi o'zgaruvchanligi) koeffitsiyenti."""
        if len(sentences) < 2:
            return 0.5
        lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]
        if not lengths:
            return 0.5
        
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        return min(1.0, std_dev / max(1.0, mean_len))

    def detect_and_grade(
        self,
        student_answer: str,
        base_academic_score: float,
        max_score: float = 100.0,
        penalty_strictness: float = 1.0
    ) -> Dict[str, Any]:
        """
        2-Yondashuv: AI-nazorati bilan mustaqil umumiy baholash.
        """
        clean_text = student_answer.strip()
        if not clean_text or len(clean_text) < 30:
            return {
                "score": 0.0,
                "max_score": max_score,
                "ai_probability": 0.0,
                "action": "Javob bo'sh",
                "penalty_factor": 0.0,
                "detected_phrases": [],
                "burstiness_score": 1.0,
                "explanation": "Matn juda qisqa yoki bo'sh."
            }

        sentences = [s.strip() for s in re.split(r'[.!?\n]', clean_text) if len(s.strip()) > 5]
        words = clean_text.split()
        
        # 1. Shablon iboralar
        detected_phrases = []
        lower_text = clean_text.lower()
        for pattern in AI_CLICHE_PATTERNS:
            matches = re.findall(pattern, lower_text)
            if matches:
                detected_phrases.extend(matches)

        cliche_count = len(detected_phrases)
        burstiness = self.calculate_burstiness(sentences)
        
        bullet_points = len(re.findall(r'(^|\n)\s*(\d+\.|\-|\*|•)\s+', clean_text))
        bullet_ratio = bullet_points / max(1, len(sentences))

        unique_words = set(w.lower() for w in words)
        ttr = len(unique_words) / max(1, len(words))

        # Integrallashgan AI ehtimolligi (0.0 dan 1.0 gacha)
        ai_score = 0.0
        ai_score += min(0.50, cliche_count * 0.14)
        
        if burstiness < 0.28:
            ai_score += 0.25
        elif burstiness < 0.38:
            ai_score += 0.12
            
        if bullet_ratio > 0.4 and len(sentences) > 4:
            ai_score += 0.20

        if 0.65 <= ttr <= 0.85 and len(words) > 50:
            ai_score += 0.10

        ai_probability = min(0.98, max(0.02, ai_score))

        # 2-Baholash: AI ta'sirida yakuniy ballni hisoblash
        if ai_probability >= 0.75 and penalty_strictness >= 0.7:
            # Agar AI generatsiyasi o'ta yuqori bo'lsa: 0 ball qo'yiladi (umuman baho qo'yilmaydi)
            score_2 = 0.0
            action = "0 BALL (BAHO BEKOR QILINDI)"
            explanation = (
                f"Topshiriqda sun'iy intellektdan (ChatGPT) ruxsatsiz to'liq foydalanilganlik "
                f"aniqlandi (Ehtimollik: {int(ai_probability * 100)}%). {len(detected_phrases)} ta AI qolipi topildi. "
                f"Shu sababli ushbu yondashuv bo'yicha 0/{max_score} qo'yildi."
            )
        elif ai_probability >= 0.35:
            # Qisman AI bo'lsa, ball pasaytiriladi
            penalty_pct = round(ai_probability * penalty_strictness, 2)
            reduced_score = base_academic_score * (1.0 - penalty_pct)
            score_2 = round(max(0.0, reduced_score), 1)
            action = f"BALL KAMAYTIRILDI (-{int(penalty_pct * 100)}%)"
            explanation = (
                f"Matnda qisman sun'iy intellekt jumlalari sezildi ({int(ai_probability * 100)}%). "
                f"Akademik baho {int(penalty_pct * 100)}% ga kamaytirilib, {score_2}/{max_score} ball belgilandi."
            )
        else:
            # Mustaqil yozilgan bo'lsa, ball to'liq saqlanadi
            score_2 = base_academic_score
            action = "BALL TO'LIQ SAQLANDI (MUSTAQIL)"
            explanation = (
                f"Matn o'quvchi tomonidan mustaqil bajarilganligi ehtimoli yuqori "
                f"(AI xavfi minimal: {int(ai_probability * 100)}%). Baho saqlandi: {score_2}/{max_score}."
            )

        return {
            "score": score_2,
            "max_score": max_score,
            "ai_probability": round(ai_probability, 2),
            "action": action,
            "detected_phrases": list(set(detected_phrases)),
            "burstiness_score": round(burstiness, 2),
            "explanation": explanation
        }
