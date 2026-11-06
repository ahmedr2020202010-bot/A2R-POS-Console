# A2R Operations Console (PySide6 Version)

## المتطلبات (Requirements)
يجب تثبيت المكتبات التالية لتشغيل البرنامج:
```bash
pip install -r requirements.txt
```

## التشغيل (Run)
لتشغيل واجهة البرنامج الجديدة المبنية على PySide6:
```bash
python main.py
```
لتجربة نافذة التقفيل بشكل منفصل:
```bash
python closing_window.py
```

## هيكل المشروع (Project Structure)
- `main.py`: النافذة الرئيسية (وضع الميني والوضع الكامل) باستخدام PySide6.
- `closing_window.py`: نافذة التقفيل (POS Closing) مع دعم التشغيل في الخلفية (QThread).
- `pos_engine.py`: محرك معالجة الإيصالات والـ OCR (يتم استدعاؤه من النوافذ).
- `requirements.txt`: المكتبات المطلوبة.

تم إعداد هذا المشروع ليكون جاهزاً للرفع على GitHub.
