import os
import sys
import time
import glob
import subprocess
from PySide6.QtCore import QThread, Signal

def get_resource_path(relative_path):
    """ الحصول على المسار الصحيح للملفات سواء أثناء التطوير أو بعد دمجها داخل الـ EXE """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AutoPrintWorker(QThread):
    printed_signal = Signal(str, int)
    error_signal = Signal(str)

    def __init__(self, watch_dir):
        super().__init__()
        self.watch_dir = watch_dir
        self.is_running = True
        self.printed_count_today = 0
        self.printed_set = set()
        
        if os.path.exists(self.watch_dir):
            for f in glob.glob(os.path.join(self.watch_dir, "*.pdf")):
                self.printed_set.add(os.path.basename(f))

    def run(self):
        while self.is_running:
            try:
                if not os.path.exists(self.watch_dir):
                    time.sleep(2)
                    continue
                    
                pdf_files = glob.glob(os.path.join(self.watch_dir, "*.pdf"))
                for pdf in pdf_files:
                    fname = os.path.basename(pdf)
                    if fname in self.printed_set:
                        continue
                        
                    if fname.lower().startswith("quote_receipt_") or fname.startswith("_"):
                        if os.path.getsize(pdf) > 1000 and not os.path.exists(pdf + ".crdownload"):
                            self.printed_set.add(fname)
                            self.print_pdf(pdf)
                            self.printed_count_today += 1
                            self.printed_signal.emit(fname, self.printed_count_today)
                            
            except Exception as e:
                self.error_signal.emit(str(e))
                
            time.sleep(2)

    def print_pdf(self, pdf_path):
        sumatra = get_resource_path("SumatraPDF.exe")
        if not os.path.exists(sumatra):
            return 
            
        cmd = [
            sumatra,
            "-print-to-default",
            "-print-settings", "paper=57 x 90 mm,fit",
            "-silent",
            pdf_path
        ]
        flags = 0
        if os.name == 'nt':
            flags = 0x08000000 
        subprocess.run(cmd, creationflags=flags)

    def stop(self):
        self.is_running = False
