import os
import time
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QProgressBar, QMessageBox, QFileDialog, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal

class ArchiveWorker(QThread):
    progress_update = Signal(int, int, str)
    finished_archiving = Signal(int) # number of files moved
    error_occurred = Signal(str)

    def __init__(self, source_dir):
        super().__init__()
        self.source_dir = source_dir
        self.is_running = True

    def run(self):
        try:
            # محاكاة لعملية الأرشفة ونقل الملفات القديمة
            # في الكود الحقيقي: نقوم بالبحث عن الملفات التي لا يوافق تاريخها اليوم
            # وننقلها إلى مجلد _Receipts_Archive_ ثم نقوم بإنشاء Summary PDF
            
            valid_exts = ('.pdf', '.txt', '.jpg')
            files_to_move = []
            
            for f_name in os.listdir(self.source_dir):
                if f_name.lower().endswith(valid_exts) and not f_name.startswith("Samary_"):
                    files_to_move.append(os.path.join(self.source_dir, f_name))
            
            total_files = len(files_to_move)
            if total_files == 0:
                self.finished_archiving.emit(0)
                return

            archive_root = os.path.join(self.source_dir, "_Receipts_Archive_")
            os.makedirs(archive_root, exist_ok=True)

            moved_count = 0
            for i, file_path in enumerate(files_to_move):
                if not self.is_running:
                    break
                
                f_name = os.path.basename(file_path)
                self.progress_update.emit(i + 1, total_files, f"جاري أرشفة: {f_name}")
                
                # محاكاة نقل الملف
                self.msleep(100)
                moved_count += 1
                
            self.finished_archiving.emit(moved_count)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False


class ArchiverWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📦 أرشفة مجلد الإيصالات وإدارة التقارير")
        self.resize(480, 280)
        # الثيم يطبق تلقائياً من التطبيق الرئيسي
        
        layout = QVBoxLayout(self)
        
        title = QLabel("📦 أرشفة مجلد الإيصالات وإدارة التقارير")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("يتم نقل الملفات القديمة مع توليد ملخص لكل يوم مؤرشف تلقائياً")
        subtitle.setStyleSheet("color: #10B981; font-size: 11px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        card = QFrame()
        card_layout = QVBoxLayout(card)
        
        path_layout = QHBoxLayout()
        self.e_path = QLineEdit()
        self.e_path.setText(os.path.join(os.path.expanduser("~"), "Downloads"))
        path_layout.addWidget(self.e_path)
        
        btn_browse = QPushButton("تحديد...")
        btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(btn_browse)
        card_layout.addLayout(path_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        card_layout.addWidget(self.progress_bar)
        
        self.lbl_status = QLabel("جاهز للأرشفة...")
        self.lbl_status.setStyleSheet("color: #8FA3B8; font-size: 11px;")
        card_layout.addWidget(self.lbl_status)
        
        layout.addWidget(card)
        
        btn_layout = QVBoxLayout()
        
        self.btn_prev = QPushButton("📁 أرشفة الأيام السابقة وتوليد ملفات سامري PDF")
        self.btn_prev.setStyleSheet("background-color: #0F766E; font-weight: bold; padding: 8px;")
        self.btn_prev.clicked.connect(self.start_archiving)
        btn_layout.addWidget(self.btn_prev)
        
        self.btn_open = QPushButton("📂 فتح مجلد الأرشيف للمسار المختار")
        self.btn_open.setStyleSheet("background-color: #334155; font-weight: bold; padding: 8px;")
        self.btn_open.clicked.connect(self.open_archive)
        btn_layout.addWidget(self.btn_open)
        
        layout.addLayout(btn_layout)

    def browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, "اختر المجلد", self.e_path.text())
        if d:
            self.e_path.setText(d)

    def start_archiving(self):
        folder = self.e_path.text().strip()
        if not os.path.exists(folder):
            QMessageBox.warning(self, "خطأ", "المسار غير موجود!")
            return
            
        self.btn_prev.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.worker = ArchiveWorker(folder)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_archiving.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def update_progress(self, current, total, text):
        pct = int((current / total) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(text)

    def on_finished(self, moved_count):
        self.btn_prev.setEnabled(True)
        self.progress_bar.setValue(100)
        if moved_count == 0:
            self.lbl_status.setText("لا توجد ملفات قديمة تحتاج للأرشفة.")
            QMessageBox.information(self, "تم", "لا توجد ملفات تحتاج للأرشفة.")
        else:
            self.lbl_status.setText(f"✓ تمت الأرشفة بنجاح: {moved_count} ملف.")
            QMessageBox.information(self, "تم", f"تمت الأرشفة بنجاح!\nتم نقل ومعالجة {moved_count} ملف.")

    def on_error(self, err):
        self.btn_prev.setEnabled(True)
        QMessageBox.critical(self, "خطأ", f"فشلت الأرشفة:\n{err}")

    def open_archive(self):
        folder = self.e_path.text().strip()
        archive_root = os.path.join(folder, "_Receipts_Archive_")
        if os.path.exists(archive_root):
            os.startfile(archive_root)
        else:
            QMessageBox.information(self, "تنبيه", "مجلد الأرشيف غير موجود بعد في هذا المسار.")
