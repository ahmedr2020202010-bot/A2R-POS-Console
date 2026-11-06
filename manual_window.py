import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

class ManualReceiptWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة معاملة يدوية (PDF)")
        self.resize(350, 300)
        self.setStyleSheet("background-color: #080E17; color: white; font-family: 'Segoe UI';")

        layout = QVBoxLayout(self)

        title = QLabel("➕ إصدار إيصال تحصيل يدوي")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Amount
        self.e_amt = QLineEdit()
        self.e_amt.setPlaceholderText("المبلغ (جنيه)*")
        self.e_amt.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42; padding: 6px;")
        layout.addWidget(self.e_amt)

        # Name
        self.e_name = QLineEdit()
        self.e_name.setPlaceholderText("اسم المؤمن له (اختياري)")
        self.e_name.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42; padding: 6px;")
        layout.addWidget(self.e_name)

        # Plate
        self.e_plate = QLineEdit()
        self.e_plate.setPlaceholderText("رقم اللوحة (اختياري)")
        self.e_plate.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42; padding: 6px;")
        layout.addWidget(self.e_plate)

        # Unit
        self.e_unit = QLineEdit()
        self.e_unit.setPlaceholderText("وحدة المرور (اختياري)")
        self.e_unit.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42; padding: 6px;")
        layout.addWidget(self.e_unit)

        layout.addStretch()

        btn_generate = QPushButton("توليد إيصال تحصيل يدوي PDF")
        btn_generate.setStyleSheet("background-color: #10B981; font-weight: bold; padding: 8px;")
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
            
        # هنا يتم استدعاء دالة بناء الـ PDF باستخدام ReportLab
        # E.create_manual_receipt_pdf(filepath, unit, plate, name, amt)
        QMessageBox.information(self, "تم", f"تم إنشاء الإيصال اليدوي بنجاح بمبلغ {amt:.2f} ج.م (هذه واجهة تجريبية).")
        self.accept()

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = ManualReceiptWindow()
    w.show()
    sys.exit(app.exec())
