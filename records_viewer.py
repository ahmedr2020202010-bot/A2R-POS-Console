import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

class RecordsViewerWindow(QDialog):
    def __init__(self, parent=None, records=None):
        super().__init__(parent)
        self.setWindowTitle("A2R - عرض السجلات ومطابقتها")
        self.resize(1100, 600)
        self.setStyleSheet("background-color: #080E17; color: white;")
        
        # In a real scenario, this data would come from the main app or database
        self.records = records if records is not None else [
            {"order": 1, "unit": "أبيس", "plate": "س ج د - 123", "name": "أحمد محمد", "amount": 1500.5, "time": "12:30", "status": "✓", "file": "rec_1.pdf"},
            {"order": 2, "unit": "برج العرب", "plate": "ب ص - 987", "name": "محمود علي", "amount": 2100.0, "time": "13:15", "status": "⚠ ملغي", "file": "rec_2.pdf"}
        ]

        layout = QVBoxLayout(self)

        # 1. Search Bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث بالاسم، اللوحة، الشاسيه...")
        self.search_input.setStyleSheet("background-color: #0A131F; padding: 6px; border: 1px solid #1E2E42;")
        self.search_input.textChanged.connect(self.filter_records)
        search_layout.addWidget(self.search_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("المبلغ...")
        self.amount_input.setFixedWidth(100)
        self.amount_input.setStyleSheet("background-color: #0A131F; padding: 6px; border: 1px solid #1E2E42;")
        self.amount_input.textChanged.connect(self.filter_records)
        search_layout.addWidget(self.amount_input)

        btn_open = QPushButton("📄 فتح الملف")
        btn_open.setStyleSheet("background-color: #0284C7; padding: 6px; font-weight: bold;")
        btn_open.clicked.connect(self.open_selected)
        search_layout.addWidget(btn_open)

        btn_void = QPushButton("❌ إلغاء المحددة")
        btn_void.setStyleSheet("background-color: #991B1B; padding: 6px; font-weight: bold;")
        btn_void.clicked.connect(self.void_selected)
        search_layout.addWidget(btn_void)
        
        btn_restore = QPushButton("↩️ استرجاع")
        btn_restore.setStyleSheet("background-color: #0F766E; padding: 6px; font-weight: bold;")
        btn_restore.clicked.connect(self.restore_selected)
        search_layout.addWidget(btn_restore)

        self.lbl_count = QLabel(f"العدد: {len(self.records)}")
        self.lbl_count.setStyleSheet("color: #38BDF8; font-weight: bold;")
        search_layout.addWidget(self.lbl_count)

        layout.addLayout(search_layout)

        # 2. Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["م", "الوحدة", "رقم اللوحة", "اسم المؤمن له", "المبلغ", "الوقت", "الحالة", "الملف"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: #0A131F; gridline-color: #1E2E42; }")
        layout.addWidget(self.table)
        
        # Context Menu for Table
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.doubleClicked.connect(self.open_selected)

        self.populate_table(self.records)

    def populate_table(self, data):
        self.table.setRowCount(len(data))
        total_amt = 0.0
        for row, rec in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(rec["order"])))
            self.table.setItem(row, 1, QTableWidgetItem(rec["unit"]))
            self.table.setItem(row, 2, QTableWidgetItem(rec["plate"]))
            self.table.setItem(row, 3, QTableWidgetItem(rec["name"]))
            self.table.setItem(row, 4, QTableWidgetItem(f"{rec['amount']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(rec["time"]))
            self.table.setItem(row, 6, QTableWidgetItem(rec["status"]))
            self.table.setItem(row, 7, QTableWidgetItem(rec["file"]))
            
            if "ملغي" not in rec["status"]:
                total_amt += rec["amount"]
                
        self.lbl_count.setText(f"العدد: {len(data)} | الصافي: {total_amt:.2f} ج.م")

    def filter_records(self):
        txt = self.search_input.text().lower()
        amt = self.amount_input.text().strip()
        
        filtered = []
        for r in self.records:
            match_txt = txt in str(r["name"]).lower() or txt in str(r["plate"]).lower() or txt in str(r["unit"]).lower()
            match_amt = True
            if amt:
                try:
                    match_amt = float(amt) == r["amount"]
                except ValueError:
                    match_amt = False
                    
            if match_txt and match_amt:
                filtered.append(r)
                
        self.populate_table(filtered)

    def show_context_menu(self, pos):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #121E2E; color: white; border: 1px solid #1E2E42; } QMenu::item:selected { background-color: #0284C7; }")
        
        open_action = QAction("📄 فتح الملف", self)
        open_action.triggered.connect(self.open_selected)
        menu.addAction(open_action)
        
        void_action = QAction("❌ إلغاء المعاملة", self)
        void_action.triggered.connect(self.void_selected)
        menu.addAction(void_action)
        
        restore_action = QAction("↩️ استرجاع", self)
        restore_action.triggered.connect(self.restore_selected)
        menu.addAction(restore_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(pos))

    def get_selected_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تنبيه", "اختر صفاً أولاً")
            return None, row
        
        # For simplicity in this mock, we get data from table items
        rec = {
            "order": self.table.item(row, 0).text(),
            "amount": float(self.table.item(row, 4).text()),
            "status": self.table.item(row, 6).text(),
        }
        return rec, row

    def open_selected(self):
        rec, _ = self.get_selected_record()
        if rec:
            QMessageBox.information(self, "فتح", f"جاري فتح الملف للمعاملة رقم {rec['order']}")
            # os.startfile(actual_path)

    def void_selected(self):
        rec, row = self.get_selected_record()
        if rec:
            if "ملغي" in rec["status"]:
                QMessageBox.information(self, "معلومة", "المعاملة ملغية بالفعل!")
                return
                
            reply = QMessageBox.question(self, "تأكيد", f"هل أنت متأكد من إلغاء المعاملة بمبلغ {rec['amount']}؟")
            if reply == QMessageBox.Yes:
                self.table.item(row, 6).setText("⚠ ملغي (يدوي)")
                self.records[row]["status"] = "⚠ ملغي (يدوي)"
                self.filter_records() # to update totals

    def restore_selected(self):
        rec, row = self.get_selected_record()
        if rec:
            if "ملغي" not in rec["status"]:
                QMessageBox.information(self, "معلومة", "المعاملة غير ملغية لتسترجعها!")
                return
                
            reply = QMessageBox.question(self, "تأكيد", f"استرجاع المعاملة بمبلغ {rec['amount']}؟")
            if reply == QMessageBox.Yes:
                self.table.item(row, 6).setText("✓")
                self.records[row]["status"] = "✓"
                self.filter_records()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = RecordsViewerWindow()
    w.show()
    sys.exit(app.exec())
