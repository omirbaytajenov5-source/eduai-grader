"""
Namunaviy topshiriqlar va javoblar (Eksperiment va sinov uchun)
Dissertatsiyaning IV bobi (Eksperimental qism) uchun tayyor keyslar.
"""

SAMPLE_TASK = """Fanning nomi: Informatika va axborot texnologiyalari.
Mavzu: Python dasturlash tilida Rekursiya tushunchasi va faktorial hisoblash.
Topshiriq:
1. Rekursiya nima ekanligini o'z so'zlaringiz bilan tushuntiring.
2. N sonining faktorialini hisoblovchi rekursiv funksiya kodini yozing.
3. Rekursiyaning cheksiz aylanib qolmasligi uchun nima qilish kerak (baza holati)?"""

SAMPLE_REFERENCE = """Etalon talablar:
- Rekursiya funksiyaning o'z-o'zini chaqirishi ekanligi aytilishi kerak.
- Bazaviy holat (base condition, masalan n <= 1 bo'lganda 1 qaytarish) aniq ko'rsatilishi shart.
- Python kodi: def factorial(n): if n <= 1: return 1; return n * factorial(n - 1)
- Agar to'xtash sharti bo'lmasa, RecursionError / stek to'lib ketishi yuz berishi tushuntirilishi lozim."""

# Keys 1: O'quvchining mustaqil mehnati (Xato bor, lekin urinish va harakat yuqori)
STUDENT_SAMPLE_EFFORT = """Menimcha rekursiya bu funksiyani o'zini ichida qayta chaqirish. 
Faktorialni hisoblash uchun dastlab urinib ko'rdim:
def faktorial(n):
    if n == 1:
        return 1
    else:
        natija = n * faktorial(n - 1)
        return natija

Bu yerda men hisoblab chiqdim, agar 5 kiritsak 5*4*3*2*1 bo'lib 120 chiqadi.
Lekin agar n = 0 kiritilsa xato bo'lishi mumkin deb o'ylayman, shuning uchun shartga 0 ni ham qo'shish kerak. 
To'xtash sharti bo'lmasa kompyuter qotib qoladi."""

# Keys 2: 100% ChatGPT tomonidan yozilgan shablon javob (Yuqori AI xavfi)
STUDENT_SAMPLE_AI = """Xulosa qilib aytganda, rekursiya dasturlashda juda muhim rol o'ynaydi va zamonaviy dunyoda algoritmlarni tushunishda beqiyos ahamiyatga ega. Keling, ko'rib chiqamiz.

Shuni ta'kidlash joizki, rekursiya — bu funksiyaning o'zini o'zi to'g'ridan-to'g'ri yoki bilvosita chaqirish jarayonidir. 

Faktorialni hisoblash uchun quyidagi mukammal Python kodi taqdim etiladi:
```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

Shubhasiz, rekursiyaning eng muhim jihati uning bazaviy holatidir (base case). Agar bazaviy holat mavjud bo'lmasa, dastur cheksiz rekursiyaga tushib, tizim xotirasini to'ldiradi. Bir tomondan bu matematik qulaylik, ikkinchi tomondan esa ehtiyotkorlikni talab etadi. Xulosa o'rnida aytish mumkinki, rekursiya universal mexanizmdir."""

# Keys 3: Zaif va qisqa javob (dangasa o'quvchi)
STUDENT_SAMPLE_WEAK = """Rekursiya bu funksiya.
def f(n): return n
To'xtash kerak."""
