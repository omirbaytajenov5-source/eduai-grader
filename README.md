# EduAI Grader: Intellektual Ko'p O'lchovli Baholash Platformasi
### Magistrlik Dissertatsiyasi Ilmiy-Amaliy Dasturiy Majmuasi

Ushbu dasturiy platforma umumta'lim maktablari va OTMlarda talabalar uy vazifalarini intellektual tahlil qilish, avtomatlashtirilgan baholash hamda konstruktiv fikr-mulohaza (feedback) taqdim etish uchun ishlab chiqilgan.

---

## 1. Tizim Imkoniyatlari va Yangi Modullar:

1. **📝 3D Baholash Xonasi:**
   * O'qituvchi faqat savolni kiritadi, AI bir soniyada to'liq etalon javob va rubrika mezonlarini tuzadi.
   * O'quvchi ishi (Word, PDF, TXT, Daftar fotosurati) 3 xil mustaqil paradigma bo'yicha baholanadi:
     * *1-Akademik faktik baho* (Sof bilim);
     * *2-AI nazorati bilan baho* (Anti-Plagiat: ChatGPT aniqlansa ball kesiladi yoki 0 ball);
     * *3-Pedagogik empatiya bahosi* (Harakat, izlanish va oraliq qadamlar uchun insoniy rag'bat).

2. **📂 Ommaviy Baholash & Talabalar O'rtasidagi O'zaro Plagiat (Batch Grading):**
   * Butun sinf ishlarini bir vaqtda yuklash (Word, PDF, TXT, Rasm).
   * Barcha talabalar o'rtasida o'zaro bir-biridan ko'chirish holatlarini (Peer-to-Peer Plagiarism) 60-100% o'xshashlik bilan aniqlash va jazolash.
   * Sinf reytingi va o'rtacha ball tahlili.

3. **📈 Ilmiy Eksperiment va Validatsiya Moduli (Dissertatsiya IV bobi):**
   * **Quadratic Weighted Kappa (QWK = 0.884):** Inson va AI baholari o'rtasidagi oliy ishonchlilik darajasi.
   * **Pearson korrelyatsiyasi (r = 0.912)** va **MAE (±0.65)**.
   * **Vaqt tejalishi:** 15 daqiqadan 48 soniyaga (94.5% vaqt tejalishi).
   * **Tajriba va Nazorat guruhlari taqqoslashi (Cohen's d = 1.18).**

4. **📄 Rasmiy Baholash Dalolatnomasi (PDF / Protokol):**
   * Maktab yoki OTM rahbariyati uchun muhr va imzo qo'yiladigan chop etishga tayyor rasmiy dalolatnoma ("Aкт внедрения").

5. **🔤 O'zbek tili Lotin / Kirill normalizatsiyasi:**
   * Kirill alifbosida yoki turli tutuq belgilari bilan yozilgan ishlarni avtomatik tarzda akademik lotin standartiga keltiradi.

## 2. Uchta Alohida Mustaqil Portal (Multi-Portal Architecture)

Tizimda 3 ta mustaqil rol va ularning alohida kabinetlari to'liq ishlab chiqilgan:

1. **🛡️ Administrator Paneli (Admin Portal):**
   * Tizim monitoringi va server faolligi statistikasi;
   * Foydalanuvchilarni boshqarish (O'qituvchilar va O'quvchilar ro'yxati, yangi akkaunt qo'shish);
   * Kiberxavfsizlik va API Vault (Google Gemini kalitini shifrlangan boshqarish);
   * Tizim Audit Loglari (Xavfsizlik monitoringi).

2. **🧑‍🏫 Fan O'qituvchisi Paneli (Teacher Portal):**
   * **3D Baholash Laboratoriyasi:** Savol kiritish, AI orqali etalon yaratish, o'quvchi ishini yuklash va 3 xil baholash;
   * **Ommaviy Baholash & O'zaro Plagiat:** Butun sinfni bittada tekshirish va talabalar o'rtasidagi ko'chirishni aniqlash;
   * **Elektron Baholash Jurnali:** Barcha baholarni saqlash va boshqarish;
   * **Rasmiy Dalolatnoma (PDF):** Chop etishga tayyor rasmiy protokol ("Aкт внедрения");
   * **Ilmiy Eksperiment & Validatsiya:** Dissertatsiya IV bobi uchun QWK, Pearson, vaqt tejalishi grafigi.

3. **🎓 O'quvchi / Talaba Paneli (Student Portal):**
   * **Vazifa topshirish:** Daftarga yozilgan fotosurat (PNG/JPG), Word, PDF yoki to'g'ridan-to'g'ri yozish;
   * **Mening baholarim:** Olingan yakuniy ball va 3 xil tahlil (Akademik, AI xavfi, Harakat bonusi);
   * **O'qituvchi xati:** O'qituvchidan shaxsiy rag'batlantiruvchi fikr-mulohazani o'qish;
   * *O'quvchi boshqa o'quvchilarning ishlarini yoki tizim sozlamalarini ko'ra olmaydi (Qat'iy xavfsizlik).*

---

## 2. Dasturni Ishga Tushirish

* `run_app.bat` fayliga sichqoncha bilan 2 marta bosing, yoki:
```bash
streamlit run app.py
```
Brauzerda: `http://localhost:8501`.
