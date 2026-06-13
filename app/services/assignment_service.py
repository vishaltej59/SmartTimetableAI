from app.database.db import get_connection


def add_assignment(user_id, title, due_date, priority="Medium", estimated_hours=1.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO assignments (user_id, title, due_date, priority, status, estimated_hours)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (user_id, title, due_date, priority, "Pending", estimated_hours),
    )
    conn.commit()
    conn.close()
    return {"message": "Assignment added successfully"}


def get_assignments(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute(
            "SELECT * FROM assignments WHERE user_id = ? ORDER BY due_date ASC",
            (user_id,),
        )
    else:
        # Default fallback for testing if no user provided
        cursor.execute("SELECT * FROM assignments ORDER BY due_date ASC")

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


def update_assignment(assignment_id, **kwargs):
    if not kwargs:
        return {"message": "No fields to update"}

    conn = get_connection()
    cursor = conn.cursor()

    query = "UPDATE assignments SET "
    updates = []
    params = []

    for key, value in kwargs.items():
        updates.append(f"{key} = ?")
        params.append(value)

    query += ", ".join(updates) + " WHERE id = ?"
    params.append(assignment_id)

    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return {"message": "Assignment updated"}


def complete_assignment(assignment_id):
    return update_assignment(assignment_id, status="Completed")


def delete_assignment(assignment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    conn.commit()
    conn.close()
    return {"message": "Assignment deleted"}
