import os
import re

# قاموس المعرفات من الكود الأصلي لربط رقم الـ TID بالوحدة
TERMINALS_MAP = {
    "53139352": "أبيس", "53139369": "أبيس", "53139371": "أبيس",
    "53139357": "برج العرب", "53139370": "برج العرب",
    "53139361": "المنتزه", "53139364": "المنتزه",
    "53139354": "محرم بك", "53139366": "محرم بك",
    "53139363": "العجمي", "53139368": "العجمي",
    "53139358": "القباري", "53139367": "القباري",
    "53139355": "مصطفى كامل", "53139362": "مصطفى كامل", "53139359": "مصطفى كامل",
    "53139353": "مديرية الأمن",
    "53139360": "ميناء الإسكندرية",
    "53139356": "خدمات مصر"
}

def extract_tid_from_text(text):
    match = re.search(r'TID:\s*(\d+)', text)
    if match:
        return match.group(1)
    
    # Fallback OCR regex if TID is printed standalone
    match = re.search(r'(53139\d{3})', text)
    if match:
        return match.group(1)
    return None

def mock_closing_scan(filepath):
    # محاكاة لعمل محرك استخراج البيانات
    # في الكود الفعلي، أنت تستخدم rapidocr أو pdf2text
    
    unit_name = "غير محدد"
    tid = None
    amount = 0.0
    
    # فحص اسم الملف فقط كحالة اختبار، لكن في البرنامج سيعمل الـ OCR
    basename = os.path.basename(filepath)
    
    # استخراج المبلغ التقريبي من اسم الملف أو النص
    amt_match = re.search(r'_(\d+\.?\d*)_', basename)
    if amt_match:
        amount = float(amt_match.group(1))
    
    # كود الـ OCR الوهمي سيحاول إيجاد أي رقم ماكينة في النص لمعرفة الوحدة
    # لكن حالياً سنكتفي بإرجاع قيمة مبدئية
    
    return {
        "unit": unit_name,
        "tid": tid,
        "amount": amount,
        "status": "✓"
    }
