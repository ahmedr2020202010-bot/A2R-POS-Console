import os
import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import arabic_reshaper
    from bidi.algorithm import get_display
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def _ar(text):
    if not text:
        return ""
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except:
        return str(text)

def create_manual_receipt_pdf(filepath, unit_val, plate_val, name_val, amt_val):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab is not installed.")
        
    op_dt = datetime.datetime.now()
    PAGE_W, PAGE_H = 160, 240
    c = canvas.Canvas(filepath, pagesize=(PAGE_W, PAGE_H))
    
    font_name = "Helvetica-Bold"
    for f_cand in [r"C:\Windows\Fontsrial.ttf", r"C:\Windows\Fonts	ahoma.ttf"]:
        if os.path.exists(f_cand):
            try:
                pdfmetrics.registerFont(TTFont("ReceiptArabic", f_cand))
                font_name = "ReceiptArabic"
                break
            except: pass

    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1.2)
    c.rect(4, 4, PAGE_W - 8, PAGE_H - 8)

    c.setFont(font_name, 13)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 20, _ar("إيصال تحصيل يدوي"))

    c.setLineWidth(0.8)
    c.roundRect(PAGE_W / 2 - 55, PAGE_H - 36, 110, 14, 3, fill=False, stroke=True)
    c.setFont(font_name, 8.5)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 33, _ar("معاملة يدوية - للمراجعة"))

    y = PAGE_H - 58
    rows = [
        ("وحدة المرور", unit_val if unit_val else "غير محدد"),
        ("اسم المؤمن له", name_val if name_val else "-"),
        ("رقم اللوحة", plate_val if plate_val else "-"),
        ("تاريخ العملية", op_dt.strftime("%d-%m-%Y")),
        ("وقت الطباعة", op_dt.strftime("%H:%M %d-%m-%Y")),
    ]

    for lbl, val in rows:
        c.setFont(font_name, 9)
        c.drawRightString(PAGE_W - 10, y, _ar(lbl))
        c.drawString(10, y, _ar(val))
        c.setLineWidth(0.4)
        c.setDash(2, 2)
        c.line(8, y - 4, PAGE_W - 8, y - 4)
        c.setDash()
        y -= 20

    box_height = 68
    box_y = y - 56
    c.setLineWidth(1.2)
    c.rect(8, box_y, PAGE_W - 16, box_height, fill=False, stroke=True)

    c.setFont(font_name, 8.5)
    c.drawCentredString(PAGE_W / 2, box_y + box_height - 14, _ar("تنبيه: إيصال تحصيل يدوي مؤقت"))
    c.setFont(font_name, 7.5)
    c.drawCentredString(PAGE_W / 2, box_y + box_height - 24, _ar("(غير معتمد نهائياً - الدفع إلكتروني فيزا POS)"))

    c.setFont(font_name, 9)
    c.drawCentredString(PAGE_W / 2, box_y + 20, _ar("المبلغ المحصل:"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PAGE_W / 2, box_y + 6, f"{amt_val:,.2f} EGP")

    c.save()

def write_excel_report(records, out_file):
    # نسخة مصغرة من دالة الإكسيل في الكود الأصلي
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Detailed Report"
    ws.views.sheetView[0].rightToLeft = True

    font_header = Font(name="Arial", size=12, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    center = Alignment(horizontal="center", vertical="center")

    headers = ["م", "وحدة المرور", "رقم اللوحة", "اسم المؤمن له", "المبلغ (جنيه)",
               "وقت الطباعة", "الحالة", "اسم الملف"]

    ws.row_dimensions[1].height = 28
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font, cell.fill, cell.alignment = font_header, fill_header, center

    for idx, rec in enumerate(records, 1):
        row_data = [
            idx, rec.get('unit', '-'), str(rec.get('plate', '-')), 
            rec.get('name', '-'), float(rec.get('amount', 0)),
            rec.get('time', '-'), rec.get('status', '-'), rec.get('file', '-')
        ]
        
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=idx+1, column=col_idx, value=val)
            cell.alignment = center
            
    for col_i in range(1, 9): 
        ws.column_dimensions[get_column_letter(col_i)].width = 20
        
    wb.save(out_file)
    return out_file
