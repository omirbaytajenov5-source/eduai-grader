"""
TALABALAR O'RTASIDAGI O'ZARO KO'ChIRIShNI ANIQLASh MODULI (Peer-to-Peer Plagiarism Checker)
Sinfdagi barcha topshirilgan ishlar o'rtasidagi semantik va leksik o'xshashlikni
juftma-juft (pairwise) tahlil qiladi va talabalar bir-biridan ko'chirganligini aniqlaydi.
"""

import re
from typing import List, Dict, Any

def get_word_shingles(text: str, k: int = 3) -> set:
    """Matnni k-shingle (3 talik ketma-ket so'zlar) to'plamiga ajratish."""
    words = [w.lower() for w in re.findall(r'\b\w+\b', text)]
    if len(words) < k:
        return set(words)
    return set(" ".join(words[i:i+k]) for i in range(len(words) - k + 1))

def calculate_jaccard_similarity(set_a: set, set_b: set) -> float:
    """Ikkita to'plam o'rtasidagi Jaccard o'xshashlik koeffitsiyenti."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / max(1, union)

class PeerPlagiarismChecker:
    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold

    def check_batch_plagiarism(self, submissions: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        submissions: [{"student_name": "Aliyev", "text": "Javob matni..."}, ...]
        Barcha talabalar o'rtasida o'zaro ko'chirishni aniqlash.
        """
        n = len(submissions)
        if n < 2:
            return {
                "flagged_pairs": [],
                "similarity_matrix": [],
                "summary": "Taqqoslash uchun kamida 2 ta talaba ishi talab etiladi."
            }

        shingles_list = [get_word_shingles(sub["text"]) for sub in submissions]
        flagged_pairs = []
        matrix = []

        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    sim = 1.0
                elif i < j:
                    sim = calculate_jaccard_similarity(shingles_list[i], shingles_list[j])
                    if sim >= self.threshold:
                        flagged_pairs.append({
                            "student_1": submissions[i]["student_name"],
                            "student_2": submissions[j]["student_name"],
                            "similarity_pct": int(sim * 100),
                            "verdict": "O'ta yuqori o'xshashlik (Ko'chirilganlik ehtimoli yuqori!)" if sim >= 0.8 else "Shubhali o'xshashlik"
                        })
                else:
                    sim = matrix[j][i]
                row.append(round(sim, 2))
            matrix.append(row)

        return {
            "flagged_pairs": flagged_pairs,
            "similarity_matrix": matrix,
            "total_checked": n,
            "flagged_count": len(flagged_pairs),
            "summary": f"{n} ta ish tekshirildi. {len(flagged_pairs)} ta shubhali o'zaro ko'chirilgan juftlik aniqlandi."
        }
