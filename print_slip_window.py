import os
import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
import reports as rep

class PrintSlipWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("طباعة إيصال تصوير")
        self.resize(350, 300)
        # Theme is applied automatically via main app
        
        layout = QVBoxLayout(self)
        
        title = QLabel("🖨️ طباعة إيصال تصوير (Slip)")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.e_name = QLineEdit()
        self.e_name.setPlaceholderText("اسم الموظف / العميل*")
        layout.addWidget(self.e_name)
        
        self.e_unit = QComboBox()
        self.e_unit.addItems([
            "أبيس", "برج العرب", "المنتزه", "محرم بك", "العجمي", 
            "القباري", "مصطفى كامل", "مديرية الأمن", "ميناء الإسكندرية", "خدمات مصر"
        ])
        layout.addWidget(self.e_unit)

        self.e_tid = QLineEdit()
        self.e_tid.setPlaceholderText("رقم الماكينة (TID) - اختياري")
        layout.addWidget(self.e_tid)
        
        layout.addStretch()
        
        btn_print = QPushButton("إنشاء وطباعة الآن")
        btn_print.setStyleSheet("background-color: #D97706; font-weight: bold; padding: 10px;")
        btn_print.clicked.connect(self.generate_slip)
        layout.addWidget(btn_print)

    def generate_slip(self):
        name = self.e_name.text().strip()
        if not name:
            QMessageBox.warning(self, "خطأ", "يجب إدخال اسم الموظف أو العميل!")
            return
        
        unit = self.e_unit.currentText()
        tid = self.e_tid.text().strip()
        date_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        file_name = f"Copy_Slip_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
        file_path = os.path.join(downloads_dir, file_name)
        
        try:
            rep.create_photocopy_slip_pdf(file_path, name, unit, date_str, tid)
            QMessageBox.information(self, "تم", "تم إنشاء إيصال التصوير بنجاح.\nسيتم فتحه الآن.")
            os.startfile(file_path)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إنشاء الإيصال:\n{e}")

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = PrintSlipWindow()
    w.show()
    sys.exit(app.exec())
