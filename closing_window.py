import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QProgressBar, 
    QMessageBox, QFileDialog, QHeaderView, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
import pos_engine as E 

class ClosingWorker(QThread):
    """
    عامل في الخلفية (Background Thread) لتنفيذ عمليات الـ OCR
    لكي لا تتجمد واجهة المستخدم أثناء قراءة الإيصالات.
    """
    progress_update = Signal(int, int, str)  # (current, total, file_name)
    finished_scan = Signal(list, list, list) # (items, warnings, excluded)
    error_occurred = Signal(str)

    def __init__(self, sources):
        super().__init__()
        self.sources = sources
        self.is_running = True

    def run(self):
        try:
            total_files = len(self.sources)
            items = []
            for i, file in enumerate(self.sources):
                if not self.is_running:
                    break
                
                self.progress_update.emit(i + 1, total_files, f"Reading: {os.path.basename(file)}")
                
                # استدعاء وهمي لمحرك القراءة (يعوض بمحركك الفعلي)
                self.msleep(300) # محاكاة للوقت
                
                items.append({
                    "order": i + 1, "unit": "أبيس", "tid": "50335710",
                    "amount": 1500.50, "date": "10.11", "status": "✓", 
                    "file": os.path.basename(file)
                })
            
            self.finished_scan.emit(items, ["تحذير: ملف غير مقروء"], [])
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False


class ClosingWindow(QDialog):
    """
    نافذة التقفيل (POS Closing) بـ PySide6
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("A2R - التقفيل")
        self.resize(850, 600)
        self.setStyleSheet("background-color: #080E17; color: white;")

        self.sources = []
        self.worker = None

        layout = QVBoxLayout(self.layout())
        
        # 1. شريط اختيار الملفات
        source_layout = QHBoxLayout()
        self.lbl_source = QLabel("لم يتم اختيار مصدر بعد")
        self.lbl_source.setStyleSheet("color: #8FA3B8; font-weight: bold;")
        source_layout.addWidget(self.lbl_source)
        
        btn_folder = QPushButton("📁 اختيار مجلد")
        btn_folder.setStyleSheet("background-color: #334155; padding: 6px;")
        btn_folder.clicked.connect(self.pick_folder)
        source_layout.addWidget(btn_folder)

        btn_files = QPushButton("🗂️ اختيار ملفات")
        btn_files.setStyleSheet("background-color: #334155; padding: 6px;")
        btn_files.clicked.connect(self.pick_files)
        source_layout.addWidget(btn_files)
        layout.addLayout(source_layout)

        # 2. أزرار التحكم وشريط التقدم
        ctrl_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ بدء القراءة")
        self.btn_start.setStyleSheet("background-color: #16A34A; font-weight: bold; padding: 8px;")
        self.btn_start.clicked.connect(self.start_processing)
        ctrl_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹ إيقاف")
        self.btn_stop.setStyleSheet("background-color: #DC2626; font-weight: bold; padding: 8px;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_processing)
        ctrl_layout.addWidget(self.btn_stop)

        layout.addLayout(ctrl_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #00FF66; }")
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

        # 3. جدول عرض النتائج
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["م", "الوحدة", "TID", "المبلغ", "التاريخ", "الحالة", "الملف"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: #0A131F; gridline-color: #1E2E42; }")
        layout.addWidget(self.table)

        # 4. صندوق الملاحظات
        self.txt_notes = QTextEdit()
        self.txt_notes.setReadOnly(True)
        self.txt_notes.setFixedHeight(80)
        self.txt_notes.setStyleSheet("background-color: #0A131F; border: 1px solid #1E2E42;")
        layout.addWidget(self.txt_notes)

        # 5. الشريط السفلي (الأزرار)
        bottom_layout = QHBoxLayout()
        btn_view = QPushButton("🔍 عرض وتعديل")
        btn_view.setStyleSheet("background-color: #D97706; padding: 6px;")
        bottom_layout.addWidget(btn_view)

        btn_rebuild = QPushButton("🔄 إعادة بناء (PDF + Excel)")
        btn_rebuild.setStyleSheet("background-color: #0284C7; padding: 6px;")
        bottom_layout.addWidget(btn_rebuild)
        
        layout.addLayout(bottom_layout)

    def pick_folder(self):
        d = QFileDialog.getExistingDirectory(self, "اختار المجلد")
        if d:
            self.sources = [d] 
            self.lbl_source.setText(f"مجلد: {d}")

    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "اختار ملفات", "", "Images/PDF (*.jpg *.png *.pdf)")
        if files:
            self.sources = files
            self.lbl_source.setText(f"تم اختيار {len(files)} ملف")

    def start_processing(self):
        if not self.sources:
            QMessageBox.warning(self, "تنبيه", "اختر مصدر الملفات أولاً")
            return

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)

        self.worker = ClosingWorker(self.sources)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_scan.connect(self.on_scan_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def stop_processing(self):
        if self.worker:
            self.worker.stop()
            self.lbl_status.setText("جاري الإيقاف...")

    def update_progress(self, current, total, text):
        pct = int((current / total) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(text)

    def on_scan_finished(self, items, warnings, excluded):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setValue(100)
        self.lbl_status.setText(f"اكتملت القراءة: {len(items)} إيصال.")

        # تعبئة الجدول
        self.table.setRowCount(len(items))
        for row, it in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(str(it["order"])))
            self.table.setItem(row, 1, QTableWidgetItem(it["unit"]))
            self.table.setItem(row, 2, QTableWidgetItem(it["tid"]))
            self.table.setItem(row, 3, QTableWidgetItem(f"{it['amount']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(it["date"]))
            self.table.setItem(row, 5, QTableWidgetItem(it["status"]))
            self.table.setItem(row, 6, QTableWidgetItem(it["file"]))

        # تعبئة الملاحظات
        if warnings:
            self.txt_notes.setText("\n".join(warnings))
        else:
            self.txt_notes.setText("لا توجد ملاحظات ✓")

    def on_error(self, err):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء القراءة:\n{err}")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = ClosingWindow()
    w.show()
    sys.exit(app.exec())
