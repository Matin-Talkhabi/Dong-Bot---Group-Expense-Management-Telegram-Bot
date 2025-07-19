import sqlite3

DB_PATH = "dong_bot.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# جدول کاربران
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")

# جدول گروه‌ها
c.execute("""
CREATE TABLE IF NOT EXISTS dongs (
    code TEXT PRIMARY KEY,
    title TEXT,
    owner_id INTEGER
)
""")

# جدول عضویت اعضا در گروه
c.execute("""
CREATE TABLE IF NOT EXISTS dong_members (
    code TEXT,
    user_id INTEGER,
    status TEXT,
    PRIMARY KEY (code, user_id)
)
""")

# جدول هزینه‌ها
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    title TEXT,
    amount REAL,
    payer_id INTEGER,
    participants TEXT
)
""")

conn.commit()
conn.close()

print("Database initialized successfully.")