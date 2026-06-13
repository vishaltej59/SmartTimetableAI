from app.database.db import get_connection


def add_study_session(exam_id, subject, session_date, planned_hours, status="PLANNED"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO study_sessions (exam_id, subject, session_date, planned_hours, completed_hours, status)
        VALUES (?, ?, ?, ?, 0.0, ?)
    """,
        (exam_id, subject, session_date, planned_hours, status),
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def update_session_status(session_id, status, completed_hours=None):
    conn = get_connection()
    cursor = conn.cursor()

    if completed_hours is not None:
        cursor.execute(
            """
            UPDATE study_sessions 
            SET status = ?, completed_hours = ? 
            WHERE id = ?
        """,
            (status, completed_hours, session_id),
        )
    else:
        cursor.execute(
            """
            UPDATE study_sessions 
            SET status = ? 
            WHERE id = ?
        """,
            (status, session_id),
        )

    conn.commit()
    conn.close()


def get_sessions_for_exam(exam_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM study_sessions WHERE exam_id = ? ORDER BY session_date ASC",
        (exam_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_study_sessions(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute(
            """
            SELECT s.* FROM study_sessions s
            JOIN exams e ON s.exam_id = e.id
            WHERE e.user_id = ?
            ORDER BY s.session_date ASC
        """,
            (user_id,),
        )
    else:
        cursor.execute("SELECT * FROM study_sessions ORDER BY session_date ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_planned_sessions_for_exam(exam_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Delete only planned sessions to avoid wiping out completed history
    cursor.execute(
        "DELETE FROM study_sessions WHERE exam_id = ? AND status = 'PLANNED'",
        (exam_id,),
    )
    conn.commit()
    conn.close()


def get_exam_readiness(exam_id, required_hours):
    """
    Calculates the readiness score for a given exam.
    Returns: dict with total_completed, total_planned, readiness_score
    """
    sessions = get_sessions_for_exam(exam_id)
    total_completed = sum(
        s["completed_hours"] for s in sessions if s["status"] == "COMPLETED"
    )

    readiness_score = 0
    if required_hours > 0:
        readiness_score = min(int((total_completed / required_hours) * 100), 100)

    return {"total_completed": total_completed, "readiness_score": readiness_score}
