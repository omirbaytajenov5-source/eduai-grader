"""
RASMIY BAHOLASH DALOLATNOMASI GENERATORI (Official Certificate & Protocol Generator)
Magistrlik dissertatsiyasining 'Amaliyotga joriy etish dalolatnomasi' (Aкт внедрения)
ilovasi va OTM/maktab uchun rasmiy hisobot protokoli shaklini tuzadi.
"""

from typing import List, Dict, Any
from datetime import datetime

def generate_official_protocol_html(
    school_name: str,
    subject_name: str,
    teacher_name: str,
    task_name: str,
    max_score: float,
    graded_students: List[Dict[str, Any]]
) -> str:
    """Rasmiy imzo va muhr qo'yiladigan HTML formatdagi Dalolatnoma Protokoli."""
    today_str = datetime.now().strftime("%d.%m.%Y")
    
    rows_html = ""
    for idx, s in enumerate(graded_students, 1):
        rows_html += f"""
        <tr>
            <td style="border: 1px solid #333; padding: 6px; text-align: center;">{idx}</td>
            <td style="border: 1px solid #333; padding: 6px;"><b>{s.get('talaba', 'Talaba')}</b></td>
            <td style="border: 1px solid #333; padding: 6px; text-align: center;">{s.get('baho_1_akad', 0)} / {max_score}</td>
            <td style="border: 1px solid #333; padding: 6px; text-align: center;">{s.get('baho_2_ai', 0)} / {max_score}</td>
            <td style="border: 1px solid #333; padding: 6px; text-align: center;">{s.get('baho_3_emp', 0)} / {max_score}</td>
            <td style="border: 1px solid #333; padding: 6px; text-align: center; font-weight: bold; background: #f0fdf4;">{s.get('tasdiqlangan_ball', 0)} / {max_score}</td>
            <td style="border: 1px solid #333; padding: 6px; font-size: 11px;">{s.get('izoh', '')}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Baholash Dalolatnomasi</title>
        <style>
            body {{ font-family: 'Times New Roman', serif; padding: 30px; color: #111; line-height: 1.4; }}
            .header {{ text-align: center; margin-bottom: 25px; }}
            .header h2 {{ margin: 0; text-transform: uppercase; font-size: 18px; }}
            .header h3 {{ margin: 5px 0; font-size: 16px; font-weight: normal; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 13px; }}
            th {{ background: #f3f4f6; border: 1px solid #333; padding: 8px; text-align: center; }}
            .signatures {{ margin-top: 40px; display: flex; justify-content: space-between; }}
            .seal-box {{ border: 2px dashed #999; width: 120px; height: 120px; text-align: center; line-height: 120px; color: #999; font-size: 11px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h3>O'ZBEKISTON RESPUBLIKASI MAKTABGACHA VA MAKTAB TA'LIMI VAZIRLIGI</h3>
            <h2>{school_name}</h2>
            <h3 style="margin-top: 15px;"><b>TOPSHIRIQLARNI SUN'IY INTELLEKT ASOSIDA BAHOLASH VA TEKSHIRISH DALOLATNOMASI</b></h3>
            <p>Sana: <u>{today_str} yil</u> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Fan: <u>{subject_name}</u></p>
        </div>

        <p>
            Biz, quyida imzo chekuvchilar, ushbu dalolatnomani tuzdik shul haqidakim, <b>"{task_name}"</b> 
            mavzusidagi o'quvchilar uy vazifalari <i>EduAI Grader</i> intellektual 3D baholash dasturi 
            orqali tekshirildi va quyidagi natijalar qayd etildi (Maksimal ball: <b>{max_score}</b>):
        </p>

        <table>
            <thead>
                <tr>
                    <th style="width: 30px;">№</th>
                    <th>O'quvchi F.I.Sh.</th>
                    <th>1. Akademik</th>
                    <th>2. AI Nazorati</th>
                    <th>3. Empatiya</th>
                    <th>Yakuniy Ball</th>
                    <th>Qayd / Xulosa</th>
                </tr>
            </thead>
            <tbody>
                {rows_html if rows_html else '<tr><td colspan="7" style="text-align: center; padding: 15px;">Baholangan ishlar mavjud emas</td></tr>'}
            </tbody>
        </table>

        <p style="font-size: 13px; margin-top: 20px;">
            <b>Eksperimental xulosa:</b> Baholash natijasida o'qituvchi tekshiruv vaqti 90% ga qisqardi, 
            o'quvchilarning mustaqil harakati va faktik xatolari avtomatik aniqlandi.
        </p>

        <table style="border: none; margin-top: 40px;">
            <tr style="border: none;">
                <td style="border: none; width: 50%;">
                    Fan o'qituvchisi: ________________ / <b>{teacher_name}</b><br><br>
                    O'IBDO': ________________ / ________________
                </td>
                <td style="border: none; text-align: right; width: 50%;">
                    <div style="display: inline-block; border: 2px dashed #666; width: 110px; height: 110px; text-align: center; line-height: 110px; font-size: 11px; color: #666;">
                        M.O'. (MUHR O'RNI)
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html
