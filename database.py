import sqlite3
import os

DB_NAME = "database.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            student_id TEXT,
            file_name TEXT,
            file_path TEXT,
            upload_time TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()

    # Insert default admin if not exists
    c.execute("SELECT * FROM admin WHERE username = '$soumen'")
    if not c.fetchone():
        c.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("$soumen", "master$3896files"))
        conn.commit()

    conn.close()

def insert_upload(student_name, student_id, file_name, file_path, upload_time):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO uploads (student_name, student_id, file_name, file_path, upload_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_name, student_id, file_name, file_path, upload_time))
    conn.commit()
    conn.close()

def validate_admin(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result

def get_all_uploads():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM uploads ORDER BY upload_time DESC")
    rows = c.fetchall()
    conn.close()
    return rows
