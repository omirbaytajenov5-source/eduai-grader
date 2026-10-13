"""
O'ZBEK TILI LOTIN-KIRILL TRANSLITERATSIYASI VA MATN NORMALIZATSIYASI MODULI
O'quvchilar tomonidan kirill yoki lotin alifbosida, shuningdek turli tutuq belgilari
(' ’ ` ´) bilan yozilgan matnlarni yagona akademik standartga keltiradi.
"""

import re

# Kirill-Lotin moslik jadvali
CYR_TO_LAT_MAP = {
    'А': 'A', 'а': 'a',
    'Б': 'B', 'б': 'b',
    'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g',
    'Д': 'D', 'д': 'd',
    'Е': 'E', 'е': 'e',
    'Ё': 'Yo', 'ё': 'yo',
    'Ж': 'J', 'ж': 'j',
    'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y',
    'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm',
    'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p',
    'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't',
    'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f',
    'Х': 'X', 'х': 'x',
    'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ch', 'ч': 'ch',
    'Ш': 'Sh', 'ш': 'sh',
    'Щ': 'Sh', 'щ': 'sh',
    'Ъ': "'", 'ъ': "'",
    'Ы': 'I', 'ы': 'i',
    'Ь': '', 'ь': '',
    'Э': 'E', 'э': 'e',
    'Ю': 'Yu', 'ю': 'yu',
    'Я': 'Ya', 'я': 'ya',
    'Ў': "O'", 'ў': "o'",
    'Қ': 'Q', 'қ': 'q',
    'Ғ': "G'", 'ғ': "g'",
    'Ҳ': 'H', 'ҳ': 'h'
}

def normalize_apostrophes(text: str) -> str:
    """Barcha nostandart tutuq va urg'u belgilarini yagona standart apostrofga keltirish."""
    return re.sub(r"[`’´‘ʻʼ]", "'", text)

def cyrillic_to_latin(text: str) -> str:
    """Kirill alifbosidagi o'zbekcha matnni to'liq lotin alifbosiga o'girish."""
    text = normalize_apostrophes(text)
    
    # Ye / E qoidasi: so'z boshida yoki unlidan keyin Ye bo'ladi
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in CYR_TO_LAT_MAP:
            result.append(CYR_TO_LAT_MAP[char])
        else:
            result.append(char)
        i += 1
        
    return "".join(result)

def normalize_uzbek_text(text: str) -> str:
    """Matnni tozalash, kirill bo'lsa lotinga o'girish va tutuq belgilarini standartlashtirish."""
    if not text:
        return ""
    # Agar matnda kirill harflari ko'p bo'lsa, lotinga o'giramiz
    cyrillic_chars = len(re.findall(r'[а-яА-ЯёЁўЎқҚғҒҳҲ]', text))
    if cyrillic_chars > 5:
        text = cyrillic_to_latin(text)
    else:
        text = normalize_apostrophes(text)
    return text.strip()
