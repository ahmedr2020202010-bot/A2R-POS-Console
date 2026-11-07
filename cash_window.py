from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QGridLayout, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

class CashWindow(QDialog):
    def __init__(self, parent=None, system_total=0.0):
        super().__init__(parent)
        self.setWindowTitle("💵 حاسبة الكاش والمطابقة")
        self.resize(450, 500)
        self.system_total = system_total
        
        layout = QVBoxLayout(self)
        
        # System Total Display
        sys_frame = QFrame()
        sys_frame.setStyleSheet("background-color: #1E293B; border-radius: 8px; padding: 10px;")
        sys_layout = QVBoxLayout(sys_frame)
        sys_title = QLabel("إجمالي السيستم المطلوب")
        sys_title.setStyleSheet("color: #94A3B8; font-weight: bold;")
        sys_title.setAlignment(Qt.AlignCenter)
        sys_layout.addWidget(sys_title)
        
        self.lbl_sys_amt = QLabel(f"{self.system_total:,.2f} ج.م")
        self.lbl_sys_amt.setStyleSheet("color: #38BDF8; font-size: 24px; font-weight: bold;")
        self.lbl_sys_amt.setAlignment(Qt.AlignCenter)
        sys_layout.addWidget(self.lbl_sys_amt)
        layout.addWidget(sys_frame)
        
        # Calculator Grid
        grid_frame = QFrame()
        grid = QGridLayout(grid_frame)
        
        self.denominations = [200, 100, 50, 20, 10, 5]
        self.inputs = {}
        self.labels = {}
        
        grid.addWidget(QLabel("الفئة"), 0, 0, alignment=Qt.AlignCenter)
        grid.addWidget(QLabel("العدد"), 0, 1, alignment=Qt.AlignCenter)
        grid.addWidget(QLabel("الإجمالي"), 0, 2, alignment=Qt.AlignCenter)
        
        for i, denom in enumerate(self.denominations, 1):
            lbl_denom = QLabel(f"فئة {denom} ج")
            lbl_denom.setStyleSheet("font-weight: bold; color: #10B981;")
            grid.addWidget(lbl_denom, i, 0)
            
            inp = QLineEdit()
            inp.setPlaceholderText("0")
            inp.setAlignment(Qt.AlignCenter)
            inp.textChanged.connect(self.calculate_cash)
            self.inputs[denom] = inp
            grid.addWidget(inp, i, 1)
            
            lbl_res = QLabel("0 ج.م")
            self.labels[denom] = lbl_res
            grid.addWidget(lbl_res, i, 2)
            
        layout.addWidget(grid_frame)
        
        # Results Area
        res_frame = QFrame()
        res_frame.setStyleSheet("background-color: #0F172A; border-radius: 8px; padding: 10px; border: 1px solid #1E293B;")
        res_layout = QVBoxLayout(res_frame)
        
        self.lbl_actual = QLabel("الفعلي في الدرج: 0.00 ج.م")
        self.lbl_actual.setStyleSheet("font-size: 16px; font-weight: bold; color: #F59E0B;")
        res_layout.addWidget(self.lbl_actual)
        
        self.lbl_diff = QLabel("العجز / الزيادة: 0.00 ج.م")
        self.lbl_diff.setStyleSheet("font-size: 16px; font-weight: bold;")
        res_layout.addWidget(self.lbl_diff)
        
        layout.addWidget(res_frame)
        
        btn_reset = QPushButton("إعادة ضبط 🔄")
        btn_reset.setStyleSheet("background-color: #334155; padding: 10px; font-weight: bold;")
        btn_reset.clicked.connect(self.reset_calc)
        layout.addWidget(btn_reset)
        
        self.calculate_cash()

    def calculate_cash(self):
        actual_total = 0.0
        
        for denom in self.denominations:
            txt = self.inputs[denom].text().strip()
            count = 0
            if txt.isdigit():
                count = int(txt)
            
            row_sum = count * denom
            actual_total += row_sum
            self.labels[denom].setText(f"{row_sum:,.2f} ج.م")
            
        self.lbl_actual.setText(f"الفعلي في الدرج: {actual_total:,.2f} ج.م")
        
        diff = actual_total - self.system_total
        
        if diff == 0:
            self.lbl_diff.setText("✅ الدرج مطابق تماماً")
            self.lbl_diff.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981;")
        elif diff > 0:
            self.lbl_diff.setText(f"📈 يوجد زيادة: {diff:,.2f} ج.م")
            self.lbl_diff.setStyleSheet("font-size: 16px; font-weight: bold; color: #3B82F6;")
        else:
            self.lbl_diff.setText(f"📉 يوجد عجز: {abs(diff):,.2f} ج.م")
            self.lbl_diff.setStyleSheet("font-size: 16px; font-weight: bold; color: #EF4444;")

    def reset_calc(self):
        for inp in self.inputs.values():
            inp.clear()
        self.calculate_cash()
