import os
import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

import database as db
import reports as rep

class ManualReceiptWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة معاملة يدوية (PDF)")
        self.resize(350, 320)
        # سيتم تطبيق الثيم تلقائياً من main.py

        layout = QVBoxLayout(self)

        title = QLabel("➕ إصدار إيصال تحصيل يدوي")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Amount
        self.e_amt = QLineEdit()
        self.e_amt.setPlaceholderText("المبلغ (جنيه)*")
        layout.addWidget(self.e_amt)

        # Name
        self.e_name = QLineEdit()
        self.e_name.setPlaceholderText("اسم المؤمن له (اختياري)")
        layout.addWidget(self.e_name)

        # Plate
        self.e_plate = QLineEdit()
        self.e_plate.setPlaceholderText("رقم اللوحة (اختياري)")
        layout.addWidget(self.e_plate)

        # Unit
        self.e_unit = QLineEdit()
        self.e_unit.setPlaceholderText("وحدة المرور (اختياري)")
        layout.addWidget(self.e_unit)

        layout.addStretch()

        btn_generate = QPushButton("توليد إيصال تحصيل يدوي PDF")
        btn_generate.setStyleSheet("background-color: #10B981; font-weight: bold; padding: 10px;")
        btn_generate.clicked.connect(self.generate_pdf)
        layout.addWidget(btn_generate)

    def generate_pdf(self):
        amt_str = self.e_amt.text().strip()
        if not amt_str:
            QMessageBox.warning(self, "خطأ", "يجب إدخال المبلغ أولاً!")
            return
            
        try:
            amt = float(amt_str)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "صيغة المبلغ غير صحيحة!")
            return
            
        unit = self.e_unit.text().strip() or "غير محدد"
        plate = self.e_plate.text().strip() or "-"
        name = self.e_name.text().strip() or "-"
        
        # 1. إعداد اسم الملف والمسار
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        file_name = f"_{amt:g}_{timestamp}.pdf"
        
        # التأكد من وجود مجلد التحميلات للحفظ
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = os.path.join(downloads_dir, file_name)

        try:
            # 2. إنشاء الـ PDF الفعلي
            rep.create_manual_receipt_pdf(file_path, unit, plate, name, amt)
            
            # 3. الحفظ في قاعدة البيانات
            db.add_manual_tx(unit, plate, name, amt, file_name)
            
            # 4. رسالة نجاح وفتح الملف
            QMessageBox.information(self, "تم", f"تم إنشاء الإيصال بنجاح بمبلغ {amt:.2f} ج.م.\nحُفظ في: التنزيلات (Downloads)")
            os.startfile(file_path)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إنشاء الإيصال:\n{str(e)}")

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # import theme
    # app.setStyleSheet(theme.GLOBAL_QSS)
    w = ManualReceiptWindow()
    w.show()
    sys.exit(app.exec())
