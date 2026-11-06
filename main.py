import sys
import os
import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QProgressBar, QMessageBox, 
    QSystemTrayIcon, QMenu, QStackedWidget, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction

import database as db
import reports as rep
import pos_engine as engine
import theme
from watchdog import AutoPrintWorker
from auth_window import AuthDialog

APP_VERSION = "v51"
APP_OWNER = "Ahmed Ramadan"

class MainProcessingWorker(QThread):
    progress_update = Signal(int, int, str)
    finished_processing = Signal(list, float, str)
    error_occurred = Signal(str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.is_running = True

    def run(self):
        try:
            valid_exts = ('.jpg', '.png', '.jpeg', '.pdf')
            files = []
            for root, dirs, f_names in os.walk(self.folder_path):
                for f in f_names:
                    if f.lower().endswith(valid_exts):
                        files.append(os.path.join(root, f))
            
            total_files = len(files)
            if total_files == 0:
                raise ValueError("لا يوجد إيصالات في هذا المجلد.")

            records = []
            total_sum = 0.0

            for i, file_path in enumerate(files):
                if not self.is_running:
                    break
                self.progress_update.emit(i + 1, total_files, f"جاري معالجة: {os.path.basename(file_path)}")
                res = engine.mock_closing_scan(file_path)
                rec = {
                    "order": i + 1,
                    "unit": res.get("unit", "غير محدد"),
                    "plate": "-",
                    "name": "-",
                    "amount": res.get("amount", 0.0),
                    "time": datetime.datetime.now().strftime("%H:%M"),
                    "status": res.get("status", "✓"),
                    "file": os.path.basename(file_path),
                    "path": file_path
                }
                records.append(rec)
                total_sum += rec["amount"]

            date_str = datetime.datetime.now().strftime("%d-%m-%Y")
            excel_path = os.path.join(db.DOCUMENTS_DIR, f"Insurance_Report_{date_str}.xlsx")
            rep.write_excel_report(records, excel_path)

            self.finished_processing.emit(records, total_sum, excel_path)
        except Exception as e:
            self.error_occurred.emit(str(e))

class A2RConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"A2R Operations Console - {APP_OWNER}")
        self.setMinimumSize(440, 240)
        db.init_db()

        self.last_detailed_records = []
        self.system_total_sum = 0.0
        self.last_generated_excel = ""
        self.is_supervisor = False
        
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
        
        # Start Auto Print Watchdog
        self.downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.print_worker = AutoPrintWorker(self.downloads_dir)
        self.print_worker.printed_signal.connect(self.on_receipt_printed)
        self.print_worker.start()

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
        
        self.lbl_print_count = QLabel("🖨️ المطبوع اليوم تلقائياً: 0 إيصال")
        self.lbl_print_count.setStyleSheet("color: #94A3B8; font-weight: bold;")
        layout.addWidget(self.lbl_print_count, alignment=Qt.AlignCenter)
        
        self.btn_mini_archive = QPushButton("📦 أرشفة التنزيلات")
        self.btn_mini_archive.setStyleSheet("background-color: #4338CA; color: white; padding: 6px; font-weight: bold; margin-top: 10px;")
        self.btn_mini_archive.clicked.connect(self.open_archiver_window)
        layout.addWidget(self.btn_mini_archive)
        
        self.btn_full_console = QPushButton("🖥️ النسخة الكاملة")
        self.btn_full_console.setStyleSheet("background-color: #DC2626; color: white; padding: 8px; font-weight: bold; margin-top: 5px;")
        self.btn_full_console.clicked.connect(self.request_full_console)
        layout.addWidget(self.btn_full_console)
        
        self.stacked_widget.addWidget(self.mini_widget)

    def setup_full_view(self):
        self.full_widget = QWidget()
        layout = QVBoxLayout(self.full_widget)
        
        header = QHBoxLayout()
        logo = QLabel("A2R")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        header.addWidget(logo)
        header.addStretch()
        
        self.lbl_role = QLabel("● USER")
        self.lbl_role.setStyleSheet("color: #10B981; font-weight: bold; border: 1px solid #10B981; padding: 4px; border-radius: 4px;")
        header.addWidget(self.lbl_role)
        
        self.btn_back_mini = QPushButton("⚡ وضع الميني")
        self.btn_back_mini.setStyleSheet("background-color: #334155;")
        self.btn_back_mini.clicked.connect(self.switch_to_mini)
        header.addWidget(self.btn_back_mini)
        layout.addLayout(header)
        
        card = QFrame()
        card_layout = QVBoxLayout(card)
        
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        default_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.path_input.setText(default_dir)
        path_layout.addWidget(self.path_input)
        
        btn_browse = QPushButton("تحديد")
        btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(btn_browse)
        card_layout.addLayout(path_layout)
        
        self.btn_run = QPushButton("⚡ بدء استخراج ومعالجة البيانات")
        self.btn_run.setStyleSheet("background-color: #10B981;")
        self.btn_run.clicked.connect(self.start_processing)
        card_layout.addWidget(self.btn_run)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        card_layout.addWidget(self.progress_bar)
        
        self.lbl_status = QLabel("جاهز")
        self.lbl_status.setStyleSheet("color: #8FA3B8; font-size: 11px;")
        card_layout.addWidget(self.lbl_status)
        
        layout.addWidget(card)
        
        mid_layout = QHBoxLayout()
        btn_view_rec = QPushButton("🔍 عرض السجلات والمطابقة")
        btn_view_rec.clicked.connect(self.open_records_viewer)
        mid_layout.addWidget(btn_view_rec)
        
        self.btn_open_excel = QPushButton("📊 فتح الإكسيل")
        self.btn_open_excel.setStyleSheet("background-color: #059669;")
        self.btn_open_excel.clicked.connect(self.open_excel)
        mid_layout.addWidget(self.btn_open_excel)
        
        btn_print_slip = QPushButton("🖨️ إيصال تصوير")
        btn_print_slip.setStyleSheet("background-color: #D97706;")
        btn_print_slip.clicked.connect(self.open_print_slip_window)
        mid_layout.addWidget(btn_print_slip)

        btn_manual = QPushButton("➕ إضافة يدوي")
        btn_manual.setStyleSheet("background-color: #0F766E;")
        btn_manual.clicked.connect(self.open_manual_window)
        mid_layout.addWidget(btn_manual)

        btn_cash = QPushButton("💵 حاسبة الكاش")
        btn_cash.setStyleSheet("background-color: #0D9488;")
        btn_cash.clicked.connect(self.open_cash_window)
        mid_layout.addWidget(btn_cash)

        layout.addLayout(mid_layout)
        layout.addStretch()
        
        self.tools_layout = QHBoxLayout()
        
        self.btn_archiver = QPushButton("📦 أرشفة التنزيلات")
        self.btn_archiver.setStyleSheet("background-color: #4338CA; color: white; padding: 6px;")
        self.btn_archiver.clicked.connect(self.open_archiver_window)
        self.tools_layout.addWidget(self.btn_archiver)
        
        self.btn_archive = QPushButton("📚 سجل الأرشيف")
        self.btn_archive.setStyleSheet("background-color: #7C3AED;")
        self.btn_archive.clicked.connect(self.open_archive_history)
        self.tools_layout.addWidget(self.btn_archive)
        
        self.btn_pos_close = QPushButton("🧾 تقفيل POS")
        self.btn_pos_close.setStyleSheet("background-color: #0F766E;")
        self.btn_pos_close.clicked.connect(self.open_closing_window)
        self.tools_layout.addWidget(self.btn_pos_close)
        
        self.btn_pos_pay = QPushButton("💳 إيصالات الدفع")
        self.btn_pos_pay.setStyleSheet("background-color: #B45309;")
        self.btn_pos_pay.clicked.connect(self.open_payments_window)
        self.tools_layout.addWidget(self.btn_pos_pay)
        
        layout.addLayout(self.tools_layout)
        self.stacked_widget.addWidget(self.full_widget)

    def request_full_console(self):
        auth = AuthDialog(self)
        if auth.exec():
            self.is_supervisor = auth.is_supervisor
            
            if self.is_supervisor:
                self.lbl_role.setText("● ADMIN")
                self.lbl_role.setStyleSheet("color: #EF4444; font-weight: bold; border: 1px solid #EF4444; padding: 4px; border-radius: 4px;")
                self.btn_open_excel.show()
                self.btn_archive.show()
                self.btn_pos_close.show()
                self.btn_pos_pay.show()
            else:
                self.lbl_role.setText("● USER")
                self.lbl_role.setStyleSheet("color: #10B981; font-weight: bold; border: 1px solid #10B981; padding: 4px; border-radius: 4px;")
                self.btn_open_excel.hide()
                self.btn_archive.hide()
                self.btn_pos_close.hide()
                self.btn_pos_pay.hide()
                
            self.switch_to_full()

    def on_receipt_printed(self, filename, total_count):
        self.lbl_print_count.setText(f"🖨️ المطبوع اليوم تلقائياً: {total_count} إيصال")

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مسار الإيصالات", self.path_input.text())
        if folder:
            self.path_input.setText(folder)

    def start_processing(self):
        folder = self.path_input.text().strip()
        if not os.path.exists(folder):
            QMessageBox.warning(self, "خطأ", "المسار غير موجود!")
            return
            
        self.btn_run.setEnabled(False)
        self.progress_bar.setValue(0)
        self.worker = MainProcessingWorker(folder)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_processing.connect(self.on_processing_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def update_progress(self, current, total, text):
        pct = int((current / total) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(text)

    def on_processing_finished(self, records, total_sum, excel_path):
        self.btn_run.setEnabled(True)
        self.progress_bar.setValue(100)
        self.last_detailed_records = records
        self.system_total_sum = total_sum
        self.last_generated_excel = excel_path
        
        # FIXED: Removed multi-line f-string that caused SyntaxError in PyInstaller
        msg = (f"تمت المعالجة بنجاح!\n"
               f"تم استخراج {len(records)} إيصال بإجمالي {total_sum:,.2f} ج.م.\n"
               f"تم إنشاء التقرير: {os.path.basename(excel_path)}")
               
        self.lbl_status.setText(f"✓ اكتملت المعالجة: {len(records)} إيصال | الإجمالي: {total_sum:,.2f} ج.م")
        QMessageBox.information(self, "تم", msg)

    def on_error(self, err):
        self.btn_run.setEnabled(True)
        QMessageBox.critical(self, "خطأ", f"فشل المعالجة:\n{err}")

    def open_excel(self):
        if self.last_generated_excel and os.path.exists(self.last_generated_excel):
            os.startfile(self.last_generated_excel)

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
        self.setFixedSize(440, 240)

    def switch_to_full(self):
        self.stacked_widget.setCurrentWidget(self.full_widget)
        self.setFixedSize(720, 520)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("A2R Console", "البرنامج يعمل في الخلفية", QSystemTrayIcon.Information, 2000)

    # --- Windows Openers ---
    def open_archiver_window(self):
        try:
            from archiver_window import ArchiverWindow
            self.archiver_win = ArchiverWindow(self)
            self.archiver_win.exec()
        except ImportError as e:
            QMessageBox.warning(self, "خطأ", f"تعذر فتح أداة الأرشفة:\n{e}")

    def open_closing_window(self):
        from closing_window import ClosingWindow
        self.cw = ClosingWindow(self)
        self.cw.exec()

    def open_payments_window(self):
        from payments_window import PaymentsWindow
        self.pw = PaymentsWindow(self)
        self.pw.exec()
            
    def open_records_viewer(self):
        from records_viewer import RecordsViewerWindow
        self.rv = RecordsViewerWindow(self, records=self.last_detailed_records)
        self.rv.exec()

    def open_cash_window(self):
        from cash_window import CashWindow
        self.cash_win = CashWindow(self, system_total=self.system_total_sum)
        self.cash_win.exec()

    def open_manual_window(self):
        from manual_window import ManualReceiptWindow
        self.man_win = ManualReceiptWindow(self)
        self.man_win.exec()

    def open_print_slip_window(self):
        from print_slip_window import PrintSlipWindow
        self.slip_win = PrintSlipWindow(self)
        self.slip_win.exec()
            
    def open_archive_history(self):
        from archive_history import ArchiveHistoryWindow
        self.arch_win = ArchiveHistoryWindow(self)
        self.arch_win.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(theme.GLOBAL_QSS) 
    window = A2RConsole()
    window.show()
    sys.exit(app.exec())
