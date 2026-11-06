import sys
import os
import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget, 
    QTableWidgetItem, QProgressBar, QMessageBox, QSystemTrayIcon,
    QMenu, QStackedWidget, QDialog, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QAction, QFont

APP_VERSION = "v51"
APP_OWNER = "Ahmed Ramadan"

class A2RConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"A2R Operations Console - {APP_OWNER}")
        self.setMinimumSize(440, 210)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.setup_mini_view()
        self.setup_full_view()
        self.setup_system_tray()
        
        # Start in Mini Mode
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
        
        # Path input
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("مسار مجلد الإيصالات...")
        self.path_input.setStyleSheet("background-color: #0A131F; padding: 6px; border: 1px solid #1E2E42; color: white;")
        path_layout.addWidget(self.path_input)
        
        btn_browse = QPushButton("تحديد")
        btn_browse.setStyleSheet("background-color: #0284C7; color: white; padding: 6px;")
        path_layout.addWidget(btn_browse)
        card_layout.addLayout(path_layout)
        
        # Action Buttons
        self.btn_run = QPushButton("⚡ بدء استخراج ومعالجة البيانات")
        self.btn_run.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        card_layout.addWidget(self.btn_run)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #1E2E42; background: #0A131F; } QProgressBar::chunk { background-color: #00FF66; }")
        card_layout.addWidget(self.progress_bar)
        
        layout.addWidget(card)
        layout.addStretch()
        
        # Tools Bar (POS Closing, Excel, etc)
        tools_layout = QHBoxLayout()
        
        btn_pos_close = QPushButton("🧾 تقفيل POS")
        btn_pos_close.setStyleSheet("background-color: #0F766E; color: white; padding: 6px;")
        tools_layout.addWidget(btn_pos_close)
        
        btn_pos_pay = QPushButton("💳 إيصالات الدفع")
        btn_pos_pay.setStyleSheet("background-color: #B45309; color: white; padding: 6px;")
        tools_layout.addWidget(btn_pos_pay)
        
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Global Dark Theme (Fusion Base)
    app.setStyle("Fusion")
    qss = """
    QMainWindow { background-color: #080E17; }
    QWidget { font-family: 'Segoe UI', Arial; color: #FFFFFF; }
    QMenu { background-color: #121E2E; color: white; border: 1px solid #1E2E42; }
    QMenu::item:selected { background-color: #0284C7; }
    QMessageBox { background-color: #121E2E; }
    """
    app.setStyleSheet(qss)
    
    window = A2RConsole()
    window.show()
    sys.exit(app.exec())
