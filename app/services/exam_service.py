from app.database.db import get_connection


def add_exam(user_id, subject, exam_date, syllabus="", preparation_hours=5.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO exams (user_id, subject, exam_date, syllabus, preparation_hours)
        VALUES (?, ?, ?, ?, ?)
    """,
        (user_id, subject, exam_date, syllabus, preparation_hours),
    )
    conn.commit()
    conn.close()
    return {"message": "Exam added successfully"}


def get_exams(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute(
            "SELECT * FROM exams WHERE user_id = ? ORDER BY exam_date ASC", (user_id,)
        )
    else:
        cursor.execute("SELECT * FROM exams ORDER BY exam_date ASC")

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_exam_by_id(exam_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_exam(exam_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    conn.commit()
    conn.close()
    return {"message": "Exam deleted"}
