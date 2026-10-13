"""
OMMAVIY BAHOLASH MODULI (Batch Grader Pipeline)
Butun sinf yoki guruh o'quvchilarining ishlarini bir vaqtda qabul qilib:
1. Matnlarni o'zbek tili lotin/kirill normalizatsiya qiladi;
2. Har bir ishni 3 ta paradigma bo'yicha mustaqil baholaydi;
3. Barcha ishlar o'rtasida o'zaro ko'chirishni (Peer-to-Peer Plagiarism) tekshiradi;
4. Sinf reytingi va umumiy hisobotini tuzadi.
"""

from typing import List, Dict, Any, Tuple
from PIL import Image

from modules.file_parser import parse_uploaded_file
from modules.transliteration import normalize_uzbek_text
from modules.engine import TriDimensionalGradingEngine
from modules.plagiarism_checker import PeerPlagiarismChecker

class BatchGrader:
    def __init__(self, gemini_api_key: str = ""):
        self.engine = TriDimensionalGradingEngine(gemini_api_key=gemini_api_key)
        self.plagiarism_checker = PeerPlagiarismChecker(threshold=0.60)

    def grade_batch_files(
        self,
        files_data: List[Tuple[str, bytes]],  # [(filename, bytes), ...]
        task_prompt: str,
        reference_solution: str,
        max_score: float = 10.0,
        beta_strictness: float = 1.0
    ) -> Dict[str, Any]:
        """Barcha fayllarni bir yo'la tahlil qilish."""
        parsed_submissions = []
        graded_results = []

        # 1. Barcha fayllarni ochish va matnga keltirish
        for filename, file_bytes in files_data:
            text, img_obj, file_type = parse_uploaded_file(file_bytes, filename)
            clean_text = normalize_uzbek_text(text)
            student_label = filename.rsplit('.', 1)[0].replace('_', ' ').capitalize()

            parsed_submissions.append({
                "student_name": student_label,
                "filename": filename,
                "text": clean_text,
                "image": img_obj,
                "file_type": file_type
            })

        # 2. O'zaro ko'chirishni (Peer Plagiarism) tekshirish
        plagiarism_report = self.plagiarism_checker.check_batch_plagiarism(parsed_submissions)

        # 3. Har bir o'quvchi ishini 3 xil baholash
        for sub in parsed_submissions:
            res = self.engine.evaluate_submission(
                task_prompt=task_prompt,
                reference_solution=reference_solution,
                student_text=sub["text"],
                max_score=max_score,
                student_image=sub["image"],
                beta_strictness=beta_strictness
            )
            
            s1 = res["scores_summary"]["score_1"]
            s2 = res["scores_summary"]["score_2"]
            s3 = res["scores_summary"]["score_3"]
            
            # Agar ushbu talaba boshqasidan ko'chirgan deb topilgan bo'lsa
            is_copier = any(
                p["student_1"] == sub["student_name"] or p["student_2"] == sub["student_name"]
                for p in plagiarism_report.get("flagged_pairs", [])
            )

            graded_results.append({
                "student_name": sub["student_name"],
                "filename": sub["filename"],
                "file_type": sub["file_type"],
                "score_1_academic": s1,
                "score_2_ai": s2,
                "score_3_empathy": s3,
                "recommended_score": s3 if s3 > s1 and s2 >= s1 else s2,
                "is_peer_plagiarized": is_copier,
                "ai_probability": res["eval_2_ai_supervised"].get("ai_probability", 0),
                "feedback": res.get("student_feedback", "")
            })

        # 4. Sinf statistikasi
        if graded_results:
            avg_score = round(sum(r["recommended_score"] for r in graded_results) / len(graded_results), 1)
            highest_score = max(r["recommended_score"] for r in graded_results)
            lowest_score = min(r["recommended_score"] for r in graded_results)
        else:
            avg_score, highest_score, lowest_score = 0, 0, 0

        return {
            "total_students": len(graded_results),
            "graded_students": graded_results,
            "plagiarism_report": plagiarism_report,
            "class_stats": {
                "average_score": avg_score,
                "highest_score": highest_score,
                "lowest_score": lowest_score,
                "max_score": max_score
            }
        }
