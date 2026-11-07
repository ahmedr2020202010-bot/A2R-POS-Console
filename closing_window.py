import os
import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt

import database as db
import reports as rep

class ClosingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧾 تقفيل أجهزة الدفع (POS Closing)")
        self.resize(750, 450)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("🧾 تقفيل وردية وإصدار تقرير POS")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info_label = QLabel("قم بإدخال تفاصيل مبيعات أجهزة الفيزا لمطابقتها مع السيستم:")
        info_label.setStyleSheet("color: #10B981; font-weight: bold;")
        layout.addWidget(info_label)
        
        # --- Form Area ---
        form_layout = QHBoxLayout()
        
        self.e_tid = QLineEdit()
        self.e_tid.setPlaceholderText("رقم الماكينة (TID)*")
        form_layout.addWidget(self.e_tid)
        
        self.e_amt = QLineEdit()
        self.e_amt.setPlaceholderText("مبلغ التقفيل (EGP)*")
        form_layout.addWidget(self.e_amt)
        
        self.e_count = QLineEdit()
        self.e_count.setPlaceholderText("عدد العمليات*")
        form_layout.addWidget(self.e_count)
        
        self.e_unit = QLineEdit()
        self.e_unit.setPlaceholderText("وحدة المرور")
        form_layout.addWidget(self.e_unit)
        
        btn_add = QPushButton("➕ إضافة للقائمة")
        btn_add.setStyleSheet("background-color: #0284C7; font-weight: bold; padding: 6px;")
        btn_add.clicked.connect(self.add_pos_record)
        form_layout.addWidget(btn_add)
        
        layout.addLayout(form_layout)
        
        # --- Table Area ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["الوحدة", "TID", "المبلغ", "العمليات", "الوقت"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # --- Bottom Area ---
        bottom_layout = QHBoxLayout()
        
        self.lbl_total = QLabel("إجمالي التقفيل: 0.00 ج.م")
        self.lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; color: #F59E0B;")
        bottom_layout.addWidget(self.lbl_total)
        
        bottom_layout.addStretch()
        
        btn_clear = QPushButton("🗑️ مسح القائمة")
        btn_clear.setStyleSheet("background-color: #DC2626;")
        btn_clear.clicked.connect(self.clear_table)
        bottom_layout.addWidget(btn_clear)
        
        btn_save = QPushButton("💾 حفظ وإصدار التقرير")
        btn_save.setStyleSheet("background-color: #10B981; font-weight: bold; padding: 10px 20px;")
        btn_save.clicked.connect(self.save_and_export)
        bottom_layout.addWidget(btn_save)
        
        layout.addLayout(bottom_layout)
        
        self.total_sum = 0.0

    def add_pos_record(self):
        tid = self.e_tid.text().strip()
        amt_str = self.e_amt.text().strip()
        count_str = self.e_count.text().strip()
        unit = self.e_unit.text().strip() or "غير محدد"
        
        if not tid or not amt_str or not count_str:
            QMessageBox.warning(self, "خطأ", "برجاء إدخال رقم الماكينة، المبلغ، وعدد العمليات!")
            return
            
        try:
            amt = float(amt_str)
            count = int(count_str)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "تأكد من كتابة الأرقام بشكل صحيح!")
            return
            
        t_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        
        self.table.setItem(row_pos, 0, QTableWidgetItem(unit))
        self.table.setItem(row_pos, 1, QTableWidgetItem(tid))
        self.table.setItem(row_pos, 2, QTableWidgetItem(f"{amt:,.2f}"))
        self.table.setItem(row_pos, 3, QTableWidgetItem(str(count)))
        self.table.setItem(row_pos, 4, QTableWidgetItem(t_time))
        
        self.total_sum += amt
        self.lbl_total.setText(f"إجمالي التقفيل: {self.total_sum:,.2f} ج.م")
        
        self.e_tid.clear()
        self.e_amt.clear()
        self.e_count.clear()
        self.e_tid.setFocus()

    def clear_table(self):
        self.table.setRowCount(0)
        self.total_sum = 0.0
        self.lbl_total.setText("إجمالي التقفيل: 0.00 ج.م")

    def save_and_export(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "تنبيه", "لا توجد بيانات لحفظها!")
            return
            
        records = []
        for row in range(self.table.rowCount()):
            rec = {
                'unit': self.table.item(row, 0).text(),
                'tid': self.table.item(row, 1).text(),
                'amount': self.table.item(row, 2).text(),
                'count': self.table.item(row, 3).text(),
                'time': self.table.item(row, 4).text()
            }
            records.append(rec)
            
        # إنشاء ملف الإكسيل لتقرير التقفيل
        date_str = datetime.datetime.now().strftime("%d-%m-%Y_%H%M")
        export_path = os.path.join(db.DOCUMENTS_DIR, f"POS_Closing_{date_str}.xlsx")
        
        try:
            # استخدام مكتبة openpyxl لإنشاء التقرير
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "POS Closing Report"
            ws.views.sheetView[0].rightToLeft = True
            
            headers = ["م", "الوحدة", "رقم الماكينة (TID)", "المبلغ", "عدد العمليات", "وقت التسجيل"]
            
            font_header = Font(name="Arial", size=12, bold=True, color="FFFFFF")
            fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
            center = Alignment(horizontal="center", vertical="center")
            
            for col, h in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=h)
                cell.font, cell.fill, cell.alignment = font_header, fill_header, center
                
            for idx, rec in enumerate(records, 1):
                row_data = [idx, rec['unit'], rec['tid'], float(rec['amount'].replace(',', '')), int(rec['count']), rec['time']]
                for col, val in enumerate(row_data, 1):
                    cell = ws.cell(row=idx+1, column=col, value=val)
                    cell.alignment = center
                    
            # إضافة صف الإجمالي
            last_row = len(records) + 2
            ws.cell(row=last_row, column=3, value="الإجمالي الكلي:").font = Font(bold=True)
            ws.cell(row=last_row, column=4, value=self.total_sum).font = Font(bold=True, color="FF0000")
            
            for col in range(1, 7):
                ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 18
                
            wb.save(export_path)
            
            QMessageBox.information(self, "نجاح", f"تم تقفيل الوردية وإصدار التقرير بنجاح!\nتم الحفظ في:\n{export_path}")
            os.startfile(export_path)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تصدير التقرير:\n{e}")
