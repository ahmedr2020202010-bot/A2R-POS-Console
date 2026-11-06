# -*- coding: utf-8 -*-
"""
A2R POS Engine (PySide6 Backend Version)
محرك قراءة وتحليل إيصالات ماكينات الدفع (التقفيل + إيصالات الدفع)
تم فصله تماماً عن واجهة المستخدم ليعمل في الخلفية (Threads)
"""
import os
import sys
import re
import math
import shutil
import tempfile
import datetime
from collections import Counter
from PIL import Image, ImageOps

# ───────────────────────── جداول الماكينات والوحدات ─────────────────────────
class TerminalInfo:
    __slots__ = ("order", "row", "unit")
    def __init__(self, order, row, unit):
        self.order, self.row, self.unit = order, row, unit

TERMINALS = {
    "50335710": TerminalInfo(1, 2, "أبيس"),
    "50335993": TerminalInfo(2, 2, "أبيس"),
    "50335987": TerminalInfo(3, 2, "أبيس"),
    "50325716": TerminalInfo(4, 3, "برج العرب"),
    "50335998": TerminalInfo(5, 3, "برج العرب"),
    "50335994": TerminalInfo(6, 3, "برج العرب"),
    "50335711": TerminalInfo(7, 3, "برج العرب"),
    "50382298": TerminalInfo(8, 4, "المنتزه"),
    "50382315": TerminalInfo(9, 4, "المنتزه"),
    "50383712": TerminalInfo(10, 4, "المنتزه"),
    "50382306": TerminalInfo(11, 5, "محرم بك"),
    "50382316": TerminalInfo(12, 5, "محرم بك"),
    "50382308": TerminalInfo(13, 6, "العجمي"),
    "50383706": TerminalInfo(14, 6, "العجمي"),
    "50382300": TerminalInfo(15, 7, "القباري"),
    "50383702": TerminalInfo(16, 8, "مصطفى كامل"),
    "50382312": TerminalInfo(17, 9, "مديرية الأمن"),
    "50383699": TerminalInfo(18, 10, "ميناء الإسكندرية"),
    "50383700": TerminalInfo(19, 11, "خدمات مصر"),
}
NUM_TO_TID = {t.order: k for k, t in TERMINALS.items()}
TID_FIX = {
    "50336994": "50335994", "50336711": "50335711", "50336998": "50335998",
    "50302316": "50382316", "50382318": "50382315", "50330987": "50335987",
    "60382308": "50382308",
}

def round2(v):
    return round(float(v) + 1e-9, 2)

def terminal_label(tid):
    t = TERMINALS.get(tid)
    return f"{t.order} - {t.unit} ({tid})" if t else (tid or "غير محدد")

# ───────────────────────── OCR Engine Setup ─────────────────────────
_OCR = {"engine": None, "name": None, "tried": False, "err": ""}

def init_ocr():
    if _OCR["tried"] and _OCR["name"]: 
        return _OCR["name"]
    _OCR["tried"] = True
    
    try:
        from rapidocr_onnxruntime import RapidOCR
        _OCR["engine"] = RapidOCR()
        _OCR["name"] = "rapidocr"
        return "rapidocr"
    except Exception as e:
        _OCR["err"] = str(e)
    return None

class OcrLine:
    __slots__ = ("text", "left", "right", "top", "bottom")
    def __init__(self, text, left, right, top, bottom):
        self.text, self.left, self.right, self.top, self.bottom = text, left, right, top, bottom
    @property
    def cy(self): return (self.top + self.bottom) / 2
    @property
    def h(self): return max(1.0, self.bottom - self.top)

def extract_lines_from_image(pil_img):
    """محرك الـ OCR: يحول الصورة لنصوص وإحداثيات"""
    name = init_ocr()
    if not name:
        raise RuntimeError("لا يوجد محرك OCR (تأكد من تثبيت rapidocr-onnxruntime)")
        
    img = ImageOps.exif_transpose(pil_img).convert("L")
    import numpy as np
    arr = np.array(img.convert("RGB"))
    res = _OCR["engine"](arr)
    
    out = []
    if res[0]:
        for box, txt, score in res[0]:
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            if str(txt).strip(): 
                out.append(OcrLine(str(txt).strip(), min(xs), max(xs), min(ys), max(ys)))
    return out

def reading_text(lines): 
    return "\n".join(l.text for l in lines)

# ───────────────────────── معالجة الـ PDF ─────────────────────────
def pdf_to_images_generator(pdf_path, dpi=200):
    try:
        import pypdfium2 as pdfium
    except ImportError:
        raise RuntimeError("يجب تثبيت pypdfium2 لقراءة ملفات PDF")
        
    pdf = pdfium.PdfDocument(pdf_path)
    try:
        for i in range(len(pdf)):
            page = pdf[i]
            scale = dpi / 72.0
            yield page.render(scale=scale).to_pil().convert("RGB")
    finally:
        pdf.close()

# ───────────────────────── دوال المعالجة الأساسية ─────────────────────────
def mock_closing_scan(file_path):
    """
    هذه دالة مبدئية لربط الواجهة بالمحرك الجديد.
    سنقوم بدمج منطق البحث عن الأرقام وتحديد الماكينة هنا.
    """
    img = Image.open(file_path) if not file_path.lower().endswith('.pdf') else next(pdf_to_images_generator(file_path))
    lines = extract_lines_from_image(img)
    text = reading_text(lines)
    
    # بحث سريع عن الـ TID كمثال
    tid = None
    for m in re.finditer(r"\b(503\d{5})\b", text):
        c = TID_FIX.get(m.group(1), m.group(1))
        if c in TERMINALS: 
            tid = c
            break
            
    # بحث سريع عن إجمالي كمثال
    amount = 0.0
    m_amt = re.search(r"TOTAL.*?(\d{1,3}(?:,\d{3})*\.\d{2})", text, re.I)
    if m_amt:
        amount = float(m_amt.group(1).replace(",", ""))
        
    order = TERMINALS[tid].order if tid else None
    unit = TERMINALS[tid].unit if tid else "غير محدد"
    
    return {
        "order": order, "unit": unit, "tid": tid,
        "amount": amount, "date": "10.11", "status": "✓" if tid else "⚠ راجع", 
        "file": os.path.basename(file_path), "skip": False, "include": True
    }
