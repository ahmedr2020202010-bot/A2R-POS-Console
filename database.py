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
        c.execute('''
            CREATE TABLE IF NOT EXISTS system_meta (
                meta_key TEXT PRIMARY KEY,
                meta_value TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

def add_manual_tx(unit, plate, insured, amount, file_name):
    conn = sqlite3.connect(DB_FILE)
    try:
        created_at = datetime.datetime.now().strftime("%d-%m-%Y %H%M%S")
        conn.execute('''
            INSERT INTO manual_tx (unit, plate, insured, amount, created_at, file_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (unit, plate, insured, float(amount), created_at, file_name))
        conn.commit()
    finally:
        conn.close()

def add_void(file_key, amount, plate, reason, username="-"):
    at = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT OR REPLACE INTO voids (file_key, amount, plate, reason, voided_at, voided_by) VALUES (?,?,?,?,?,?)",
                     (file_key, float(amount), plate or "-", reason or "", at, username))
        conn.commit()
    finally:
        conn.close()
