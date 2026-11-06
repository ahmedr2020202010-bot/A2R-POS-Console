import sqlite3
import os
import datetime

# إعداد مسار قاعدة البيانات
DOCUMENTS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "A2R_Reports")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
DB_FILE = os.path.join(DOCUMENTS_DIR, "a2r_vault.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        # جدول المعاملات اليدوية
        c.execute('''
            CREATE TABLE IF NOT EXISTS manual_tx (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit TEXT,
                plate TEXT,
                insured TEXT,
                amount REAL,
                created_at TEXT,
                file_name TEXT
            )
        ''')
        # جدول الإلغاءات
        c.execute('''
            CREATE TABLE IF NOT EXISTS voids (
                file_key TEXT PRIMARY KEY,
                amount REAL,
                plate TEXT,
                reason TEXT,
                voided_at TEXT,
                voided_by TEXT
            )
        ''')
        # جدول إعدادات النظام
        c.execute('''
            CREATE TABLE IF NOT EXISTS system_meta (
                meta_key TEXT PRIMARY KEY,
                meta_value TEXT
            )
        ''')
        
        # جدول فهرس الأرشيف
        c.execute('''
            CREATE TABLE IF NOT EXISTS archive_index (
                path TEXT PRIMARY KEY, day TEXT, file TEXT, unit TEXT, plate TEXT,
                insured TEXT, amount REAL, rec_time TEXT, is_manual INTEGER,
                is_void INTEGER, is_receipt INTEGER, mtime REAL, size INTEGER
            )
        ''')
        c.execute("CREATE INDEX IF NOT EXISTS idx_arch_day ON archive_index(day)")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

def add_void(file_key, amount, plate, reason, username="-"):
    at = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT OR REPLACE INTO voids (file_key, amount, plate, reason, voided_at, voided_by) VALUES (?,?,?,?,?,?)",
                     (file_key, float(amount), plate or "-", reason or "", at, username))
        conn.commit()
    finally:
        conn.close()

def remove_void(file_key):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM voids WHERE file_key = ?", (file_key,))
        conn.commit()
    finally:
        conn.close()

def load_void_map():
    mp = {}
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT file_key, reason, voided_at, voided_by FROM voids")
        for k, r, at, by in c.fetchall():
            mp[k] = {"reason": r or "", "at": at or "", "by": by or ""}
        conn.close()
    except Exception as e:
        print(f"Load Void Map Error: {e}")
    return mp

def save_meta(key, value):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT OR REPLACE INTO system_meta (meta_key, meta_value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Save Meta Error: {e}")

def get_meta(key):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT meta_value FROM system_meta WHERE meta_key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Get Meta Error: {e}")
        return None
