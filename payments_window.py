import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QProgressBar,
    QMessageBox, QFileDialog, QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal
import pos_engine as E

class PaymentsWorker(QThread):
    progress_update = Signal(int, int, str)
    finished_scan = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, sources):
        super().__init__()
        self.sources = sources
        self.is_running = True

    def run(self):
        try:
            total = len(self.sources)
            results = []
            for i, file in enumerate(self.sources):
                if not self.is_running:
                    break
                
                self.progress_update.emit(i + 1, total, f"فحص: {os.path.basename(file)}")
                self.msleep(300) # استدعاء الفحص الحقيقي من محرك الـ OCR هنا
                
                results.append({
                    "order": i + 1, "unit": "محرم بك", "tid": "50382306",
                    "date": "12.11", "count": 25, "new_name": f"11.محرم بك.يوم.12.11",
                    "notes": "✓", "file": os.path.basename(file), "src": file
                })
            self.finished_scan.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False

class PaymentsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("A2R - إيصالات الدفع")
        self.resize(950, 650)
        self.setStyleSheet("background-color: #080E17; color: white;")
        
        self.sources = []
        self.worker = None

        layout = QVBoxLayout(self)

        # 1. Header / File Selection
        src_layout = QHBoxLayout()
        self.lbl_source = QLabel("لم يتم اختيار ملفات PDF بعد")
        self.lbl_source.setStyleSheet("color: #8FA3B8; font-weight: bold;")
        src_layout.addWidget(self.lbl_source)

        btn_files = QPushButton("🗂️ اختيار ملفات PDF")
        btn_files.setStyleSheet("background-color: #334155; padding: 6px;")
        btn_files.clicked.connect(self.pick_files)
        src_layout.addWidget(btn_files)
        layout.addLayout(src_layout)

        # 2. Controls & Progress
        ctrl_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ بدء الفحص والعد")
        self.btn_start.setStyleSheet("background-color: #16A34A; font-weight: bold; padding: 8px;")
        self.btn_start.clicked.connect(self.start_scan)
        ctrl_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹ إيقاف")
        self.btn_stop.setStyleSheet("background-color: #DC2626; font-weight: bold; padding: 8px;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_scan)
        ctrl_layout.addWidget(self.btn_stop)
        layout.addLayout(ctrl_layout)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setStyleSheet("QProgressBar::chunk { background-color: #00FF66; }")
        layout.addWidget(self.progress)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

        # 3. Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["م", "الوحدة", "TID", "التاريخ", "العدد", "الاسم الجديد", "ملاحظات", "الملف الأصلي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QTableWidget { background-color: #0A131F; gridline-color: #1E2E42; }")
        layout.addWidget(self.table)

        # 4. Footer & Actions
        self.lbl_totals = QLabel("الإجمالي: 0 إيصال")
        self.lbl_totals.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_totals)

        bottom_layout = QHBoxLayout()
        btn_edit = QPushButton("✏️ تعديل المحدد")
        btn_edit.setStyleSheet("background-color: #D97706; padding: 6px;")
        bottom_layout.addWidget(btn_edit)

        btn_save = QPushButton("💾 حفظ نسخ بالأسماء الجديدة")
        btn_save.setStyleSheet("background-color: #0F766E; padding: 6px;")
        bottom_layout.addWidget(btn_save)

        btn_export = QPushButton("📊 تصدير ملخص إكسيل")
        btn_export.setStyleSheet("background-color: #4338CA; padding: 6px;")
        bottom_layout.addWidget(btn_export)

        layout.addLayout(bottom_layout)

    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "اختار ملفات", "", "PDF Files (*.pdf)")
        if files:
            self.sources = files
            self.lbl_source.setText(f"تم اختيار {len(files)} ملف PDF")

    def start_scan(self):
        if not self.sources:
            QMessageBox.warning(self, "تنبيه", "اختر ملفات PDF أولاً")
            return
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.table.setRowCount(0)
        self.progress.setValue(0)

        self.worker = PaymentsWorker(self.sources)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_scan.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def stop_scan(self):
        if self.worker:
            self.worker.stop()
            self.lbl_status.setText("جاري الإيقاف...")

    def update_progress(self, current, total, text):
        pct = int((current / total) * 100)
        self.progress.setValue(pct)
        self.lbl_status.setText(text)

    def on_finished(self, results):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress.setValue(100)
        self.lbl_status.setText(f"تم فحص {len(results)} ملف.")

        self.table.setRowCount(len(results))
        total_count = 0
        for r, res in enumerate(results):
            self.table.setItem(r, 0, QTableWidgetItem(str(res["order"])))
            self.table.setItem(r, 1, QTableWidgetItem(res["unit"]))
            self.table.setItem(r, 2, QTableWidgetItem(res["tid"]))
            self.table.setItem(r, 3, QTableWidgetItem(res["date"]))
            self.table.setItem(r, 4, QTableWidgetItem(str(res["count"])))
            self.table.setItem(r, 5, QTableWidgetItem(res["new_name"]))
            self.table.setItem(r, 6, QTableWidgetItem(res["notes"]))
            self.table.setItem(r, 7, QTableWidgetItem(res["file"]))
            total_count += res["count"]
        
        self.lbl_totals.setText(f"الإجمالي: {total_count} إيصال")

    def on_error(self, err):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        QMessageBox.critical(self, "خطأ", f"حدث خطأ:\n{err}")

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = PaymentsWindow()
    w.show()
    sys.exit(app.exec())
