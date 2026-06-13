# Database Architecture

The Smart Timetable AI uses SQLite (`data/database.db`) for lightweight local storage.

## ER Diagram (Conceptual)
`users` (1) --- (<) `assignments`
`users` (1) --- (<) `exams`
`users` (1) --- (<) `scheduled_sessions`
`exams` (1) --- (<) `study_sessions`

## Tables

### `users`
Core user identity.
- `id` (PK, INTEGER)
- `email` (TEXT, UNIQUE)
- `name` (TEXT)
- `created_at` (TIMESTAMP)

### `assignments`
Academic tasks with deadlines.
- `id` (PK, INTEGER)
- `user_id` (FK -> users.id)
- `title` (TEXT)
- `due_date` (TEXT)
- `priority` (TEXT: Low/Medium/High)
- `status` (TEXT: Pending/Completed)
- `estimated_hours` (REAL)

### `exams`
Major exam events requiring distributed study time.
- `id` (PK, INTEGER)
- `user_id` (FK -> users.id)
- `subject` (TEXT)
- `exam_date` (TEXT)
- `syllabus` (TEXT)
- `preparation_hours` (REAL)

### `study_sessions`
Fine-grained study blocks tracking planner compliance.
- `id` (PK, INTEGER)
- `exam_id` (FK -> exams.id)
- `subject` (TEXT)
- `session_date` (TEXT)
- `planned_hours` (REAL)
- `completed_hours` (REAL)
- `status` (TEXT: PLANNED/IN_PROGRESS/COMPLETED/MISSED)
- `created_at` (TIMESTAMP)

### `scheduled_sessions`
Records linking local events to Google Calendar.
- `id` (PK, INTEGER)
- `user_id` (FK -> users.id)
- `reference_id` (INTEGER)
- `reference_type` (TEXT)
- `start_time` (TEXT)
- `end_time` (TEXT)
- `event_id` (TEXT, Google Event ID)
