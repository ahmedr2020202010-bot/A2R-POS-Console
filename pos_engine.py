# -*- coding: utf-8 -*-
"""
A2R POS Engine (PySide6 Backend Version)
يحتوي على دوال الـ OCR وتحليل ملفات الـ PDF
"""
import os
import re

# يمكن إضافة محتوى محرك الـ OCR بالكامل هنا كما كان في _A2R_POS_ENGINE_SRC
TERMINALS = {
    "50335710": {"order": 1, "row": 2, "unit": "أبيس"},
    "50335993": {"order": 2, "row": 2, "unit": "أبيس"},
    "50335987": {"order": 3, "row": 2, "unit": "أبيس"},
    "50325716": {"order": 4, "row": 3, "unit": "برج العرب"},
    "50335998": {"order": 5, "row": 3, "unit": "برج العرب"},
    "50335994": {"order": 6, "row": 3, "unit": "برج العرب"},
    "50335711": {"order": 7, "row": 3, "unit": "برج العرب"},
    "50382298": {"order": 8, "row": 4, "unit": "المنتزه"},
    "50382315": {"order": 9, "row": 4, "unit": "المنتزه"},
    "50383712": {"order": 10, "row": 4, "unit": "المنتزه"},
    "50382306": {"order": 11, "row": 5, "unit": "محرم بك"},
    "50382316": {"order": 12, "row": 5, "unit": "محرم بك"},
    "50382308": {"order": 13, "row": 6, "unit": "العجمي"},
    "50383706": {"order": 14, "row": 6, "unit": "العجمي"},
    "50382300": {"order": 15, "row": 7, "unit": "القباري"},
    "50383702": {"order": 16, "row": 8, "unit": "مصطفى كامل"},
    "50382312": {"order": 17, "row": 9, "unit": "مديرية الأمن"},
    "50383699": {"order": 18, "row": 10, "unit": "ميناء الإسكندرية"},
    "50383700": {"order": 19, "row": 11, "unit": "خدمات مصر"},
}

def analyze_receipt(file_path):
    # Dummy processing function - replace with actual OCR logic
    return {"status": "success", "amount": 100.0, "terminal": "50335710"}
