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
        
        layout = QVBoxLayout(self)
        
        title = QLabel("🖨️ طباعة إيصال تصوير (Slip)")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.e_name = QLineEdit()
        self.e_name.setPlaceholderText("اسم الموظف / العميل*")
        layout.addWidget(self.e_name)
        
        # Mapping exactly from original structure: Units to Terminal IDs
        self.unit_map = {
            "أبيس 1": "53139352",
            "أبيس 2": "53139369",
            "أبيس 3": "53139371",
            "برج العرب 1": "53139357",
            "برج العرب 2": "53139370",
            "المنتزه 1": "53139361",
            "المنتزه 2": "53139364",
            "محرم بك 1": "53139354",
            "محرم بك 2": "53139366",
            "العجمي 1": "53139363",
            "العجمي 2": "53139368",
            "القباري 1": "53139358",
            "القباري 2": "53139367",
            "مصطفى كامل 1": "53139355",
            "مصطفى كامل 2": "53139362",
            "مصطفى كامل 3": "53139359",
            "مديرية الأمن 1": "53139353",
            "ميناء الإسكندرية 1": "53139360",
            "خدمات مصر 1": "53139356"
        }
        
        self.e_unit = QComboBox()
        self.e_unit.addItems(list(self.unit_map.keys()))
        self.e_unit.currentIndexChanged.connect(self.update_terminal_id)
        layout.addWidget(self.e_unit)

        self.e_tid = QLineEdit()
        self.e_tid.setPlaceholderText("رقم الماكينة (TID) - يتم تحديده تلقائياً")
        self.e_tid.setReadOnly(True)
        self.e_tid.setStyleSheet("background-color: #1E293B; color: #94A3B8;")
        layout.addWidget(self.e_tid)
        
        layout.addStretch()
        
        btn_print = QPushButton("إنشاء وطباعة الآن")
        btn_print.setStyleSheet("background-color: #D97706; font-weight: bold; padding: 10px;")
        btn_print.clicked.connect(self.generate_slip)
        layout.addWidget(btn_print)
        
        # Trigger first update manually
        self.update_terminal_id()

    def update_terminal_id(self):
        selected_unit = self.e_unit.currentText()
        tid = self.unit_map.get(selected_unit, "")
        self.e_tid.setText(tid)

    def generate_slip(self):
        name = self.e_name.text().strip()
        if not name:
            QMessageBox.warning(self, "خطأ", "يجب إدخال اسم الموظف أو العميل!")
            return
        
        # Remove the number from unit name for printing, so "أبيس 1" becomes "أبيس"
        full_unit = self.e_unit.currentText()
        print_unit = full_unit.split(" ")[0] if " " in full_unit else full_unit
        
        tid = self.e_tid.text().strip()
        date_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        file_name = f"Copy_Slip_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
        file_path = os.path.join(downloads_dir, file_name)
        
        try:
            rep.create_photocopy_slip_pdf(file_path, name, print_unit, date_str, tid)
            QMessageBox.information(self, "تم", "تم إنشاء إيصال التصوير بنجاح.\nسيتم فتحه الآن.")
            os.startfile(file_path)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إنشاء الإيصال:\n{e}")
