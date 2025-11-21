import sqlite3

DB = "todo.db"

schema = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'done')) NOT NULL DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db(db_path=DB):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(schema)
    conn.commit()
    conn.close()
    print("Initialized DB:", db_path)

if __name__ == "__main__":
    init_db()
