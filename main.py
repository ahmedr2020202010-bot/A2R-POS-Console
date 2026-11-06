import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QProgressBar, QMessageBox, 
    QSystemTrayIcon, QMenu, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

APP_VERSION = "v51"
APP_OWNER = "Ahmed Ramadan"

class A2RConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"A2R Operations Console - {APP_OWNER}")
        self.setMinimumSize(440, 210)
        
        self.system_total_sum = 2500.50 # Dummy system total for testing
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.setup_mini_view()
        self.setup_full_view()
        self.setup_system_tray()
        
        self.switch_to_mini()

    def setup_mini_view(self):
        self.mini_widget = QWidget()
        layout = QVBoxLayout(self.mini_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("A2R Mini Station")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        status = QLabel("● محرك الطباعة الفورية يعمل بنشاط")
        status.setStyleSheet("color: #10B981; font-weight: bold; margin-top: 10px;")
        layout.addWidget(status, alignment=Qt.AlignCenter)
        
        self.btn_full_console = QPushButton("🖥️ النسخة الكاملة")
        self.btn_full_console.setCursor(Qt.PointingHandCursor)
        self.btn_full_console.setStyleSheet("background-color: #DC2626; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        self.btn_full_console.clicked.connect(self.switch_to_full)
        layout.addWidget(self.btn_full_console)
        
        self.stacked_widget.addWidget(self.mini_widget)

    def setup_full_view(self):
        self.full_widget = QWidget()
        layout = QVBoxLayout(self.full_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QHBoxLayout()
        logo = QLabel("A2R")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        header.addWidget(logo)
        header.addStretch()
        
        self.btn_back_mini = QPushButton("⚡ وضع الميني")
        self.btn_back_mini.setStyleSheet("background-color: #334155; color: white; padding: 6px; border-radius: 4px;")
        self.btn_back_mini.clicked.connect(self.switch_to_mini)
        header.addWidget(self.btn_back_mini)
        layout.addLayout(header)
        
        # Main Dashboard Area
        card = QFrame()
        card.setStyleSheet("background-color: #121E2E; border: 1px solid #1E2E42; border-radius: 8px;")
        card_layout = QVBoxLayout(card)
        
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("مسار مجلد الإيصالات...")
        self.path_input.setStyleSheet("background-color: #0A131F; padding: 6px; border: 1px solid #1E2E42; color: white;")
        path_layout.addWidget(self.path_input)
        
        btn_browse = QPushButton("تحديد")
        btn_browse.setStyleSheet("background-color: #0284C7; color: white; padding: 6px;")
        path_layout.addWidget(btn_browse)
        card_layout.addLayout(path_layout)
        
        self.btn_run = QPushButton("⚡ بدء استخراج ومعالجة البيانات")
        self.btn_run.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        card_layout.addWidget(self.btn_run)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #1E2E42; background: #0A131F; } QProgressBar::chunk { background-color: #00FF66; }")
        card_layout.addWidget(self.progress_bar)
        
        layout.addWidget(card)
        
        # Middle Bar (View Records & Daily Tools)
        mid_layout = QHBoxLayout()
        btn_view_rec = QPushButton("🔍 عرض السجلات والمطابقة")
        btn_view_rec.setStyleSheet("background-color: #0284C7; color: white; padding: 8px; font-weight: bold;")
        btn_view_rec.clicked.connect(self.open_records_viewer)
        mid_layout.addWidget(btn_view_rec)

        btn_manual = QPushButton("➕ إضافة يدوي")
        btn_manual.setStyleSheet("background-color: #0F766E; color: white; padding: 8px;")
        btn_manual.clicked.connect(self.open_manual_window)
        mid_layout.addWidget(btn_manual)

        btn_cash = QPushButton("💵 حاسبة الكاش")
        btn_cash.setStyleSheet("background-color: #0D9488; color: white; padding: 8px;")
        btn_cash.clicked.connect(self.open_cash_window)
        mid_layout.addWidget(btn_cash)

        layout.addLayout(mid_layout)
        
        layout.addStretch()
        
        # Tools Bar
        tools_layout = QHBoxLayout()
        
        self.btn_pos_close = QPushButton("🧾 تقفيل POS")
        self.btn_pos_close.setStyleSheet("background-color: #0F766E; color: white; padding: 6px;")
        self.btn_pos_close.clicked.connect(self.open_closing_window)
        tools_layout.addWidget(self.btn_pos_close)
        
        self.btn_pos_pay = QPushButton("💳 إيصالات الدفع")
        self.btn_pos_pay.setStyleSheet("background-color: #B45309; color: white; padding: 6px;")
        self.btn_pos_pay.clicked.connect(self.open_payments_window)
        tools_layout.addWidget(self.btn_pos_pay)
        
        layout.addLayout(tools_layout)
        self.stacked_widget.addWidget(self.full_widget)

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        tray_menu = QMenu()
        restore_action = QAction("فتح البرنامج", self)
        restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(restore_action)
        quit_action = QAction("إغلاق البرنامج نهائياً", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def switch_to_mini(self):
        self.stacked_widget.setCurrentWidget(self.mini_widget)
        self.setFixedSize(440, 210)

    def switch_to_full(self):
        self.stacked_widget.setCurrentWidget(self.full_widget)
        self.setFixedSize(700, 500)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("A2R Console", "البرنامج يعمل في الخلفية", QSystemTrayIcon.Information, 2000)

    # --- Windows Openers ---
    def open_closing_window(self):
        try:
            from closing_window import ClosingWindow
            self.cw = ClosingWindow(self)
            self.cw.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر فتح نافذة التقفيل:\n{e}")

    def open_payments_window(self):
        try:
            from payments_window import PaymentsWindow
            self.pw = PaymentsWindow(self)
            self.pw.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر فتح نافذة إيصالات الدفع:\n{e}")
            
    def open_records_viewer(self):
        try:
            from records_viewer import RecordsViewerWindow
            self.rv = RecordsViewerWindow(self)
            self.rv.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر فتح نافذة السجلات:\n{e}")

    def open_cash_window(self):
        try:
            from cash_window import CashWindow
            self.cash_win = CashWindow(self, system_total=self.system_total_sum)
            self.cash_win.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر فتح حاسبة الكاش:\n{e}")

    def open_manual_window(self):
        try:
            from manual_window import ManualReceiptWindow
            self.man_win = ManualReceiptWindow(self)
            self.man_win.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر فتح الإضافة اليدوية:\n{e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    qss = """
    QMainWindow { background-color: #080E17; }
    QWidget { font-family: 'Segoe UI', Arial; color: #FFFFFF; }
    QMenu { background-color: #121E2E; color: white; border: 1px solid #1E2E42; }
    QMenu::item:selected { background-color: #0284C7; }
    QMessageBox { background-color: #121E2E; }
    QDialog { background-color: #080E17; }
    """
    app.setStyleSheet(qss)
    window = A2RConsole()
    window.show()
    sys.exit(app.exec())
