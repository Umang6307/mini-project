import sqlite3
import os
from pathlib import Path
from backend.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(force_reset=False):
    db_file = Path(Config.DATABASE_PATH)
    if force_reset and db_file.exists():
        try:
            db_file.unlink()
        except Exception as e:
            print(f"Error resetting database file: {e}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Execute schema
    if os.path.exists(Config.SCHEMA_PATH):
        with open(Config.SCHEMA_PATH, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())

    # 2. Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM crops;")
    crop_count = cursor.fetchone()[0]

    if crop_count == 0:
        if os.path.exists(Config.SEED_PATH):
            with open(Config.SEED_PATH, 'r', encoding='utf-8') as f:
                cursor.executescript(f.read())

        if os.path.exists(Config.DEMO_DATA_PATH):
            with open(Config.DEMO_DATA_PATH, 'r', encoding='utf-8') as f:
                cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("Database initialized successfully at", Config.DATABASE_PATH)

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    if rv:
        res = [dict(ix) for ix in rv]
        return res[0] if one else res
    return None if one else []

def execute_db(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def execute_many(query, list_of_args):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executemany(query, list_of_args)
    conn.commit()
    conn.close()
