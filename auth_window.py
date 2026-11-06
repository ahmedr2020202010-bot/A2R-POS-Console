import hashlib
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

# Hashes from original code
SUPERVISOR_HASHES = {hashlib.sha256("a2r1000".encode('utf-8')).hexdigest()}
EMPLOYEE_PASSWORDS = [
    "ahmedramadan", "a2r", "ahmed.r", "1531", "20262", "2026", "16061993", 
    "1558", "1964", "2212", "1672", "30881999", "1990", "27121996", "1012",
    "160388", "505022", "20272", "0100elkok", "12345", "8110"
]
EMPLOYEE_HASHES = {hashlib.sha256(p.encode('utf-8')).hexdigest() for p in EMPLOYEE_PASSWORDS}

class AuthDialog(QDialog):
    def __init__(self, parent=None, admin_only=False):
        super().__init__(parent)
        self.setWindowTitle("A2R Authorization")
        self.setFixedSize(360, 200)
        self.admin_only = admin_only
        self.is_supervisor = False
        self.is_authenticated = False
        
        layout = QVBoxLayout(self)
        
        title = QLabel("A2R OPERATIONS")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        sub = QLabel("🔒 أدخل كلمة المرور" if not admin_only else "🔒 مطلوب باسورد المشرف")
        sub.setStyleSheet("color: #8FA3B8; font-weight: bold;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)
        
        pwd_layout = QHBoxLayout()
        self.e_pwd = QLineEdit()
        self.e_pwd.setEchoMode(QLineEdit.Password)
        self.e_pwd.setAlignment(Qt.AlignCenter)
        self.e_pwd.setStyleSheet("font-size: 14px; font-weight: bold; padding: 6px;")
        self.e_pwd.returnPressed.connect(self.check_pwd)
        pwd_layout.addWidget(self.e_pwd)
        
        self.btn_eye = QPushButton("👁️")
        self.btn_eye.setFixedWidth(40)
        self.btn_eye.clicked.connect(self.toggle_eye)
        pwd_layout.addWidget(self.btn_eye)
        layout.addLayout(pwd_layout)
        
        self.lbl_err = QLabel("")
        self.lbl_err.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 11px;")
        self.lbl_err.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_err)
        
        btn_enter = QPushButton("دخول 🖥️")
        btn_enter.setStyleSheet("background-color: #DC2626; font-weight: bold; padding: 8px;")
        btn_enter.clicked.connect(self.check_pwd)
        layout.addWidget(btn_enter)
        
        self.pwd_visible = False

    def toggle_eye(self):
        if self.pwd_visible:
            self.e_pwd.setEchoMode(QLineEdit.Password)
            self.btn_eye.setText("👁️")
            self.pwd_visible = False
        else:
            self.e_pwd.setEchoMode(QLineEdit.Normal)
            self.btn_eye.setText("🙈")
            self.pwd_visible = True

    def check_pwd(self):
        val = self.e_pwd.text().strip().lower()
        h_val = hashlib.sha256(val.encode('utf-8')).hexdigest()
        
        if h_val in SUPERVISOR_HASHES:
            self.is_supervisor = True
            self.is_authenticated = True
            self.accept()
        elif h_val in EMPLOYEE_HASHES and not self.admin_only:
            self.is_supervisor = False
            self.is_authenticated = True
            self.accept()
        else:
            self.lbl_err.setText("كلمة المرور غير صحيحة!")
            self.e_pwd.clear()
