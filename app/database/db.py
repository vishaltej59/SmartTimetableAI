from app.config import Config
import sqlite3
import os


def get_connection():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # We need to alter the assignments table if it doesn't have estimated_hours and user_id.
    # To handle SQLite alter limitations, we'll try to add columns and catch exceptions if they exist.
    try:
        cursor.execute(
            "ALTER TABLE assignments ADD COLUMN user_id INTEGER REFERENCES users(id)"
        )
    except sqlite3.OperationalError:
        pass  # Column might already exist

    try:
        cursor.execute(
            "ALTER TABLE assignments ADD COLUMN estimated_hours REAL DEFAULT 1.0"
        )
    except sqlite3.OperationalError:
        pass

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        title TEXT NOT NULL,
        due_date TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Pending',
        estimated_hours REAL DEFAULT 1.0
    )
    """
    )

    # Exams Table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        subject TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        syllabus TEXT,
        preparation_hours REAL DEFAULT 5.0
    )
    """
    )

    # Scheduled Sessions Table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS scheduled_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        reference_id INTEGER,
        reference_type TEXT, -- 'assignment' or 'exam'
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        event_id TEXT -- Google Calendar Event ID
    )
    """
    )

    # Insert a default user for local testing if none exists
    cursor.execute("SELECT id FROM users LIMIT 1")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (email, name) VALUES ('localuser@example.com', 'Local User')"
        )

    # Study Sessions Table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER REFERENCES exams(id),
        subject TEXT NOT NULL,
        session_date TEXT NOT NULL,
        planned_hours REAL NOT NULL,
        completed_hours REAL DEFAULT 0.0,
        status TEXT DEFAULT 'PLANNED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    conn.commit()
    conn.close()
