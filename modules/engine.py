"""
MARKAZIY GIBRID ORKESTRATOR (Tri-Paradigm Grading Engine)
O'qituvchi tomonidan belgilangan to'liq ball (max_score, masalan 10, 20 yoki 100 ball)
asosida 3 ta mustaqil umumiy baholashni amalga oshiradi:

1-BOSQICH: Umumiy Akademik & Faktik Baholash (Klassik rubrika va etalon bo'yicha)
2-BOSQICH: Umumiy AI Nazoratli Baholash (ChatGPT aniqlansa kamaytiriladi yoki 0 ball bo'ladi)
3-BOSQICH: Umumiy Pedagogik Empatiya Baholash ("O'qituvchi o'rniga o'zini qo'yib", harakat va urinish uchun rag'bat)
"""

import json
import os
from typing import Dict, Any, Optional
from PIL import Image

from modules.academic_evaluator import AcademicEvaluator
from modules.ai_detector import AIDetector
from modules.empathy_evaluator import EmpathyEvaluator

class TriDimensionalGradingEngine:
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.academic_evaluator = AcademicEvaluator()
        self.ai_detector = AIDetector()
        self.empathy_evaluator = EmpathyEvaluator()
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.has_llm = bool(self.api_key.strip())
        
        if self.has_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.genai = genai
            except Exception:
                self.has_llm = False

    def evaluate_submission(
        self,
        task_prompt: str,
        reference_solution: str,
        student_text: str,
        max_score: float = 10.0,
        student_image: Optional[Image.Image] = None,
        beta_strictness: float = 1.0,
        force_offline: bool = False
    ) -> Dict[str, Any]:
        """
        Topshiriqni 3 ta mustaqil umumiy paradigma bo'yicha baholash.
        max_score: O'qituvchi belgilagan to'liq ball (masalan: 10, 20, 100 ball).
        """
        is_image_present = student_image is not None

        if self.has_llm and not force_offline:
            try:
                return self._evaluate_with_gemini(
                    task_prompt, reference_solution, student_text, max_score, student_image, beta_strictness
                )
            except Exception as e:
                res = self._evaluate_offline(
                    task_prompt, reference_solution, student_text, max_score, is_image_present, beta_strictness
                )
                res["engine_mode"] = f"Lokal Gibrid (API xatosi: {str(e)[:40]})"
                return res
        else:
            res = self._evaluate_offline(
                task_prompt, reference_solution, student_text, max_score, is_image_present, beta_strictness
            )
            res["engine_mode"] = "Lokal Gibrid NLP (100% Bepul va Mustaqil)"
            return res

    def _evaluate_offline(
        self,
        task_prompt: str,
        reference_solution: str,
        student_text: str,
        max_score: float,
        is_image: bool,
        beta: float
    ) -> Dict[str, Any]:
        """Offline rejimda 3 ta alohida umumiy baholash."""
        
        # 1-BOSQICH: Akademik va Faktik Baholash (max_score shkalasida)
        eval_1 = self.academic_evaluator.evaluate_offline(
            task_prompt, reference_solution, student_text, max_score=max_score
        )
        score_1 = eval_1["score"]

        # 2-BOSQICH: AI Nazoratli Baholash (max_score shkalasida)
        eval_2 = self.ai_detector.detect_and_grade(
            student_text, base_academic_score=score_1, max_score=max_score, penalty_strictness=beta
        )
        score_2 = eval_2["score"]

        # 3-BOSQICH: Pedagogik Empatiya va Harakat Bahosi (max_score shkalasida)
        eval_3 = self.empathy_evaluator.evaluate_with_empathy(
            student_text, base_academic_score=score_1, max_score=max_score, is_handwritten_or_image=is_image
        )
        score_3 = eval_3["score"]

        # O'quvchiga tavsiya xati
        feedback = self._generate_feedback(score_1, score_2, score_3, max_score, eval_2, eval_3)

        return {
            "max_score": max_score,
            "eval_1_academic": eval_1,
            "eval_2_ai_supervised": eval_2,
            "eval_3_empathy": eval_3,
            "scores_summary": {
                "score_1": score_1,
                "score_2": score_2,
                "score_3": score_3,
                "max_score": max_score
            },
            "student_feedback": feedback,
            "engine_mode": "Lokal Gibrid NLP"
        }

    def _evaluate_with_gemini(
        self,
        task_prompt: str,
        reference_solution: str,
        student_text: str,
        max_score: float,
        student_image: Optional[Image.Image],
        beta: float
    ) -> Dict[str, Any]:
        """Multimodal LLM (Gemini) orqali 3 ta alohida baholash."""
        prompt = f"""
Sen ta'lim sifatini baholovchi tajribali professor va hakamisan.
Topshiriqning umumiy maksimal bali: {max_score} ball.

O'quvchining ishini 3 TA ALOHIDA va MUSTAQIL BOSQICHDA to'liq bahola:

[TOPShIRIQ]: {task_prompt}
[ETALON MEZON]: {reference_solution}
[O'QUVChI JAVOBI]: {student_text}

3 TA ALOHIDA BAHOLASH TALABI:
1-BOSQICH (Akademik Baho): Faqat yozilgan faktlar, qadamlar va etalonga moslik bo'yicha to'liq baho (0 dan {max_score} gacha).
2-BOSQICH (AI Nazoratli Baho): Agar o'quvchi ChatGPT/AI'dan foydalangan bo'lsa, ballni qisqartir, agar to'liq AI bo'lsa 0/{max_score} ball qo'y. Mustaqil yozgan bo'lsa 1-bahoni saqla.
3-BOSQICH (O'qituvchi Empatiyasi Bahosi): O'qituvchi o'rniga o'zingni qo'y. Agar o'quvchi xato qilgan bo'lsa ham mustaqil harakat qilgan, o'z so'zlari bilan uringan bo'lsa rag'batlantiruvchi odil baho ber (0 dan {max_score} gacha).

Faqat quyidagi JSON formatida javob ber:
{{
  "score_1": {round(max_score * 0.75, 1)},
  "analysis_1": "Akademik tahlil",
  "score_2": {round(max_score * 0.4, 1)},
  "action_2": "AI tufayli ball kamaytirildi",
  "ai_probability": 0.2,
  "detected_phrases": [],
  "score_3": {round(max_score * 0.85, 1)},
  "explanation_3": "Mustaqil harakat uchun rag'batlantirildi",
  "student_feedback": "O'quvchiga tavsiya xati"
}}
"""
        model = self.genai.GenerativeModel("gemini-1.5-flash")
        contents = [prompt]
        if student_image is not None:
            contents.append(student_image)

        response = model.generate_content(contents)
        raw_text = response.text.strip()
        
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()

        data = json.loads(raw_text)

        s1 = float(data.get("score_1", round(max_score * 0.7, 1)))
        s2 = float(data.get("score_2", round(max_score * 0.5, 1)))
        s3 = float(data.get("score_3", round(max_score * 0.8, 1)))

        return {
            "max_score": max_score,
            "eval_1_academic": {
                "score": s1,
                "max_score": max_score,
                "percentage": int((s1 / max_score) * 100),
                "detailed_analysis": data.get("analysis_1", ""),
                "strengths": ["Faktik javob berilgan."],
                "mistakes": []
            },
            "eval_2_ai_supervised": {
                "score": s2,
                "max_score": max_score,
                "ai_probability": float(data.get("ai_probability", 0.1)),
                "action": data.get("action_2", "Tahlil qilindi"),
                "detected_phrases": data.get("detected_phrases", []),
                "explanation": "AI ehtimolligi va originallik tekshirildi."
            },
            "eval_3_empathy": {
                "score": s3,
                "max_score": max_score,
                "grit_level": "Pedagogik tahlil",
                "explanation": data.get("explanation_3", "O'qituvchi empatiyasi bilan baholandi.")
            },
            "scores_summary": {
                "score_1": s1,
                "score_2": s2,
                "score_3": s3,
                "max_score": max_score
            },
            "student_feedback": data.get("student_feedback", "O'qishda davom eting!"),
            "engine_mode": "Multimodal Vision-LLM (Google Gemini)"
        }

    def _generate_feedback(self, s1: float, s2: float, s3: float, max_s: float, eval_2: dict, eval_3: dict) -> str:
        lines = []
        lines.append(f"Hurmatli o'quvchi! Topshirig'ingiz 3 ta mezon bo'yicha ko'rib chiqildi (Maksimal ball: {max_s}).")
        lines.append(f"1. Akademik faktik bilimingiz: {s1}/{max_s}")
        lines.append(f"2. Akademik halollik (AI nazorati): {s2}/{max_s}")
        lines.append(f"3. Mustaqil harakat va urinishingiz: {s3}/{max_s}")
        
        if eval_2.get("ai_probability", 0) >= 0.60:
            lines.append("⚠️ Eslatma: Javobingizda ChatGPT qoliplari aniqlandi. Keyingi topshiriqlarda o'z mustaqil so'zlaringiz bilan yozing.")
        elif s3 > s1:
            lines.append("🌟 Rahmat: Yechimdagi xatolarga qaramay, mustaqil uringaningiz va shaxsiy fikringiz uchun o'qituvchi sizga yuqori rag'bat bahosi qo'ydi!")

        lines.append("Xatolar ustida ishlab, bilim olishda davom eting!")
        return "\n\n".join(lines)
