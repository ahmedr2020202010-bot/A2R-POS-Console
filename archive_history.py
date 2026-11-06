import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QMenu, QTabWidget, QWidget, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

class ArchiveHistoryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("A2R - سجل الأرشيف")
        self.resize(1100, 650)
        self.setStyleSheet("background-color: #080E17; color: white;")

        layout = QVBoxLayout(self)

        # Top Bar
        bar = QHBoxLayout()
        status_lbl = QLabel("جاهز")
        status_lbl.setStyleSheet("color: #38BDF8; font-weight: bold;")
        bar.addWidget(status_lbl)
        bar.addStretch()

        btn_refresh = QPushButton("🔄 تحديث + نسخ احتياطي")
        btn_refresh.setStyleSheet("background-color: #0284C7; padding: 6px;")
        btn_refresh.clicked.connect(lambda: status_lbl.setText("تم التحديث (محاكاة)"))
        bar.addWidget(btn_refresh)

        btn_backup = QPushButton("🗄️ فتح النسخة الاحتياطية")
        btn_backup.setStyleSheet("background-color: #4338CA; padding: 6px;")
        btn_backup.clicked.connect(self.open_backup)
        bar.addWidget(btn_backup)
        layout.addLayout(bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #1E2E42; background: #0A131F; } QTabBar::tab { background: #121E2E; color: white; padding: 8px; border: 1px solid #1E2E42; } QTabBar::tab:selected { background: #0284C7; }")
        
        # Tab 1: Days
        self.tab_days = QWidget()
        self.setup_days_tab()
        self.tabs.addTab(self.tab_days, "📅 الأيام")

        # Tab 2: Global Search
        self.tab_search = QWidget()
        self.setup_search_tab()
        self.tabs.addTab(self.tab_search, "🔎 بحث عام في الأرشيف")

        layout.addWidget(self.tabs)

    def setup_days_tab(self):
        layout = QVBoxLayout(self.tab_days)
        
        filter_layout = QHBoxLayout()
        self.day_q = QLineEdit()
        self.day_q.setPlaceholderText("ابحث عن يوم (مثال: 15-10-2026)")
        self.day_q.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; padding: 4px;")
        filter_layout.addWidget(self.day_q)

        filter_layout.addWidget(QLabel("الشهر:"))
        self.cb_month = QComboBox()
        self.cb_month.addItems(["الكل", "2026-11", "2026-10"])
        self.cb_month.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; padding: 4px;")
        filter_layout.addWidget(self.cb_month)

        filter_layout.addWidget(QLabel("من:"))
        self.from_e = QLineEdit()
        self.from_e.setPlaceholderText("YYYY-MM-DD")
        self.from_e.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; padding: 4px;")
        filter_layout.addWidget(self.from_e)

        filter_layout.addWidget(QLabel("إلى:"))
        self.to_e = QLineEdit()
        self.to_e.setPlaceholderText("YYYY-MM-DD")
        self.to_e.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; padding: 4px;")
        filter_layout.addWidget(self.to_e)

        btn_clear = QPushButton("مسح الفلاتر")
        btn_clear.setStyleSheet("background-color: #64748B; padding: 4px;")
        btn_clear.clicked.connect(self.clear_day_filters)
        filter_layout.addWidget(btn_clear)

        layout.addLayout(filter_layout)

        self.day_table = QTableWidget(2, 7)
        self.day_table.setHorizontalHeaderLabels(["التاريخ", "عدد المعاملات", "إجمالي المبلغ", "يدوي", "ملغي", "مكرر", "ناقص"])
        self.day_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.day_table.setStyleSheet("QTableWidget { background-color: #0A131F; gridline-color: #1E2E42; }")
        
        # Mock Data
        self.day_table.setItem(0, 0, QTableWidgetItem("06-11-2026"))
        self.day_table.setItem(0, 1, QTableWidgetItem("150"))
        self.day_table.setItem(0, 2, QTableWidgetItem("45000.50"))
        self.day_table.setItem(0, 3, QTableWidgetItem("2"))
        self.day_table.setItem(0, 4, QTableWidgetItem("1"))
        self.day_table.setItem(0, 5, QTableWidgetItem("0"))
        self.day_table.setItem(0, 6, QTableWidgetItem("0"))
        
        self.day_table.setItem(1, 0, QTableWidgetItem("05-11-2026"))
        self.day_table.setItem(1, 1, QTableWidgetItem("120"))
        self.day_table.setItem(1, 2, QTableWidgetItem("36000.00"))
        
        layout.addWidget(self.day_table)

        self.sum_lbl = QLabel("الأيام: 2 | إجمالي المعاملات: 270 | إجمالي المبلغ: 81000.50 جنيه")
        self.sum_lbl.setStyleSheet("color: #38BDF8; font-weight: bold;")
        layout.addWidget(self.sum_lbl)

    def setup_search_tab(self):
        layout = QVBoxLayout(self.tab_search)
        
        search_layout = QHBoxLayout()
        self.s_entry = QLineEdit()
        self.s_entry.setPlaceholderText("اسم المؤمن له / رقم اللوحة / المبلغ...")
        self.s_entry.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; padding: 4px;")
        search_layout.addWidget(self.s_entry)

        self.inc_void = QCheckBox("إظهار الملغي")
        self.inc_void.setChecked(True)
        search_layout.addWidget(self.inc_void)

        self.s_count = QLabel("النتائج: 0")
        self.s_count.setStyleSheet("color: #38BDF8; font-weight: bold;")
        search_layout.addWidget(self.s_count)
        
        layout.addLayout(search_layout)

        self.search_table = QTableWidget(0, 8)
        self.search_table.setHorizontalHeaderLabels(["يوم الأرشيف", "الوحدة", "اللوحة", "المؤمن له", "المبلغ", "الوقت", "الحالة", "الملف"])
        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.search_table.setStyleSheet("QTableWidget { background-color: #0A131F; gridline-color: #1E2E42; }")
        layout.addWidget(self.search_table)

    def clear_day_filters(self):
        self.day_q.clear()
        self.from_e.clear()
        self.to_e.clear()
        self.cb_month.setCurrentIndex(0)

    def open_backup(self):
        QMessageBox.information(self, "تنبيه", "لا توجد مساحة احتياطية مهيئة حالياً (وضع المحاكاة).")

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = ArchiveHistoryWindow()
    w.show()
    sys.exit(app.exec())
