import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, 
    QLineEdit, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

class CashWindow(QDialog):
    def __init__(self, parent=None, system_total=0.0):
        super().__init__(parent)
        self.setWindowTitle("تسوية النقدية والـ POS - A2R")
        self.resize(450, 600)
        self.setStyleSheet("background-color: #080E17; color: white; font-family: 'Segoe UI';")
        self.system_total = system_total

        layout = QVBoxLayout(self)

        title = QLabel("💵 تسوية الخزينة (كاش + POS)")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        sys_lbl = QLabel(f"إجمالي سيستم التأمين المطلوب: {self.system_total:,.2f} ج.م")
        sys_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #10B981; margin-bottom: 10px;")
        sys_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(sys_lbl)

        # Cash Denominations
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; border-radius: 8px;")
        grid_layout = QGridLayout(grid_frame)

        self.denoms = {
            200: QLineEdit(),
            100: QLineEdit(),
            50: QLineEdit(),
            20: QLineEdit(),
            10: QLineEdit(),
            5: QLineEdit(),
            1: QLineEdit(),
            0.5: QLineEdit()
        }

        row = 0
        for val, le in self.denoms.items():
            lbl = QLabel(f"فئة {val} ج:")
            lbl.setStyleSheet("font-size: 12px; font-weight: bold; border: none;")
            
            le.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42; padding: 4px; color: white;")
            le.setPlaceholderText("العدد...")
            le.textChanged.connect(self.calculate_totals)
            
            grid_layout.addWidget(lbl, row, 0)
            grid_layout.addWidget(le, row, 1)
            row += 1

        layout.addWidget(grid_frame)

        # POS & External Cash
        extra_frame = QFrame()
        extra_frame.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; border-radius: 8px; margin-top: 5px;")
        extra_layout = QVBoxLayout(extra_frame)

        pos_layout = QHBoxLayout()
        pos_lbl = QLabel("إجمالي الـ POS (فيزا):")
        pos_lbl.setStyleSheet("font-weight: bold; border: none;")
        self.pos_input = QLineEdit()
        self.pos_input.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42; padding: 4px;")
        self.pos_input.textChanged.connect(self.calculate_totals)
        pos_layout.addWidget(pos_lbl)
        pos_layout.addWidget(self.pos_input)
        extra_layout.addLayout(pos_layout)

        manual_cash_layout = QHBoxLayout()
        manual_lbl = QLabel("مبلغ كاش إضافي (يدوي):")
        manual_lbl.setStyleSheet("font-weight: bold; border: none;")
        self.manual_cash_input = QLineEdit()
        self.manual_cash_input.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42; padding: 4px;")
        self.manual_cash_input.textChanged.connect(self.calculate_totals)
        manual_cash_layout.addWidget(manual_lbl)
        manual_cash_layout.addWidget(self.manual_cash_input)
        extra_layout.addLayout(manual_cash_layout)

        layout.addWidget(extra_frame)

        # Totals & Differences
        self.lbl_total_cash = QLabel("إجمالي الكاش: 0.00 ج.م")
        self.lbl_total_cash.setStyleSheet("font-size: 13px; font-weight: bold; color: #38BDF8;")
        self.lbl_total_cash.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_total_cash)

        self.lbl_total_combined = QLabel("المجموع الإجمالي (كاش + POS): 0.00 ج.م")
        self.lbl_total_combined.setStyleSheet("font-size: 14px; font-weight: bold; color: #F59E0B;")
        self.lbl_total_combined.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_total_combined)

        self.lbl_diff = QLabel("")
        self.lbl_diff.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.lbl_diff.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_diff)

        btn_close = QPushButton("إغلاق")
        btn_close.setStyleSheet("background-color: #DC2626; padding: 8px; font-weight: bold;")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

        self.calculate_totals()

    def calculate_totals(self):
        total_cash = 0.0
        
        # Calculate from denominations
        for val, le in self.denoms.items():
            txt = le.text().strip()
            if txt:
                try:
                    count = float(txt)
                    total_cash += val * count
                except ValueError:
                    pass
        
        # Add manual cash
        manual_txt = self.manual_cash_input.text().strip()
        if manual_txt:
            try: total_cash += float(manual_txt)
            except ValueError: pass

        self.lbl_total_cash.setText(f"إجمالي الكاش: {total_cash:,.2f} ج.م")

        # Get POS Total
        pos_total = 0.0
        pos_txt = self.pos_input.text().strip()
        if pos_txt:
            try: pos_total = float(pos_txt)
            except ValueError: pass

        combined = total_cash + pos_total
        self.lbl_total_combined.setText(f"المجموع الإجمالي (كاش + POS): {combined:,.2f} ج.م")

        # Compare with System
        diff = combined - self.system_total
        
        if self.system_total == 0:
            self.lbl_diff.setText("")
        elif abs(diff) < 0.01:
            self.lbl_diff.setText("✓ مطابق لسيستم التأمين تماماً")
            self.lbl_diff.setStyleSheet("font-size: 15px; font-weight: bold; color: #10B981;")
        elif diff < 0:
            self.lbl_diff.setText(f"عجز: {abs(diff):,.2f} ج.م ⚠️")
            self.lbl_diff.setStyleSheet("font-size: 15px; font-weight: bold; color: #EF4444;")
        else:
            self.lbl_diff.setText(f"زيادة: +{diff:,.2f} ج.م ⚠️")
            self.lbl_diff.setStyleSheet("font-size: 15px; font-weight: bold; color: #F59E0B;")

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = CashWindow(system_total=1500.0)
    w.show()
    sys.exit(app.exec())
