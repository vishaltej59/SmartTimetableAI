from database import get_connection

def add_assignment(title, due_date, priority="Medium"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assignments (title, due_date, priority, status)
        VALUES (?, ?, ?, ?)
    """, (title, due_date, priority, "Pending"))

    conn.commit()
    conn.close()

    return {"message": "Assignment added successfully"}


def get_assignments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assignments ORDER BY due_date ASC")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "due_date": r[2],
            "priority": r[3],
            "status": r[4]
        }
        for r in rows
    ]


def complete_assignment(assignment_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE assignments
        SET status = ?
        WHERE id = ?
    """, ("Completed", assignment_id))

    conn.commit()
    conn.close()

    return {"message": "Assignment marked as completed"}


def delete_assignment(assignment_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))

    conn.commit()
    conn.close()

    return {"message": "Assignment deleted"}