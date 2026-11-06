import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QProgressBar, 
    QMessageBox, QFileDialog, QHeaderView, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
import pos_engine as E 

class ClosingWorker(QThread):
    progress_update = Signal(int, int, str)
    finished_scan = Signal(list, list, list)
    error_occurred = Signal(str)

    def __init__(self, sources):
        super().__init__()
        self.sources = sources
        self.is_running = True

    def run(self):
        try:
            total_files = len(self.sources)
            items = []
            warnings = []
            
            for i, file_path in enumerate(self.sources):
                if not self.is_running:
                    break
                
                self.progress_update.emit(i + 1, total_files, f"جاري قراءة: {os.path.basename(file_path)}")
                
                # ------ هنا نستخدم المحرك الفعلي ------
                try:
                    result = E.mock_closing_scan(file_path)
                    items.append(result)
                    if not result["tid"]:
                        warnings.append(f"الملف {os.path.basename(file_path)}: لم يتم التعرف على الماكينة.")
                except Exception as ex:
                    warnings.append(f"الملف {os.path.basename(file_path)}: فشلت القراءة ({str(ex)})")
                # --------------------------------------
                
            self.finished_scan.emit(items, warnings, [])
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False

class ClosingWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("A2R - التقفيل")
        self.resize(850, 600)
        self.setStyleSheet("background-color: #080E17; color: white;")
        
        self.sources = []
        layout = QVBoxLayout(self)
        
        # UI Setup
        source_layout = QHBoxLayout()
        self.lbl_source = QLabel("لم يتم اختيار مصدر بعد")
        source_layout.addWidget(self.lbl_source)
        
        btn_folder = QPushButton("📁 اختيار مجلد")
        btn_folder.clicked.connect(self.pick_folder)
        source_layout.addWidget(btn_folder)

        btn_files = QPushButton("🗂️ اختيار ملفات")
        btn_files.clicked.connect(self.pick_files)
        source_layout.addWidget(btn_files)
        layout.addLayout(source_layout)

        ctrl_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶ بدء القراءة")
        self.btn_start.setStyleSheet("background-color: #16A34A; padding: 8px; font-weight: bold;")
        self.btn_start.clicked.connect(self.start_processing)
        ctrl_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹ إيقاف")
        self.btn_stop.setStyleSheet("background-color: #DC2626; padding: 8px; font-weight: bold;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_processing)
        ctrl_layout.addWidget(self.btn_stop)
        layout.addLayout(ctrl_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("")
        layout.addWidget(self.lbl_status)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["م", "الوحدة", "TID", "المبلغ", "التاريخ", "الحالة", "الملف"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.txt_notes = QTextEdit()
        self.txt_notes.setReadOnly(True)
        self.txt_notes.setFixedHeight(80)
        layout.addWidget(self.txt_notes)

    def pick_folder(self):
        d = QFileDialog.getExistingDirectory(self, "اختار المجلد")
        if d: 
            # جلب كل الصور والملفات من المجلد
            valid_exts = ('.jpg', '.png', '.jpeg', '.pdf')
            files = []
            for root, dirs, f_names in os.walk(d):
                for f in f_names:
                    if f.lower().endswith(valid_exts):
                        files.append(os.path.join(root, f))
            self.sources = files
            self.lbl_source.setText(f"مجلد: {d} ({len(files)} ملف)")

    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "اختار", "", "Images/PDF (*.jpg *.png *.pdf)")
        if files: 
            self.sources = files
            self.lbl_source.setText(f"اخترت {len(files)} ملف")

    def start_processing(self):
        if not self.sources: return
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.table.setRowCount(0)
        
        self.worker = ClosingWorker(self.sources)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.finished_scan.connect(self.on_scan_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def stop_processing(self):
        if self.worker: self.worker.stop()

    def update_progress(self, current, total, text):
        self.progress_bar.setValue(int((current/total)*100))
        self.lbl_status.setText(text)

    def on_scan_finished(self, items, warnings, excluded):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.table.setRowCount(len(items))
        
        total_amount = 0.0
        
        for row, it in enumerate(items):
            order_str = str(it["order"]) if it["order"] else "-"
            tid_str = str(it["tid"]) if it["tid"] else "-"
            
            self.table.setItem(row, 0, QTableWidgetItem(order_str))
            self.table.setItem(row, 1, QTableWidgetItem(it["unit"]))
            self.table.setItem(row, 2, QTableWidgetItem(tid_str))
            self.table.setItem(row, 3, QTableWidgetItem(f"{it['amount']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(it["date"]))
            self.table.setItem(row, 5, QTableWidgetItem(it["status"]))
            self.table.setItem(row, 6, QTableWidgetItem(it["file"]))
            
            total_amount += it["amount"]
            
        self.lbl_status.setText(f"تم الانتهاء! الإجمالي: {total_amount:.2f} ج.م")
        
        if warnings:
            self.txt_notes.setText("\n".join(warnings))
        else:
            self.txt_notes.setText("لا توجد ملاحظات ✓")
            
    def on_error(self, err):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        QMessageBox.critical(self, "خطأ", f"حدث خطأ:\n{err}")
