# Study Planner Logic

## Overview
The `planner_service.py` handles the core algorithm that translates `preparation_hours` into concrete Google Calendar events without causing conflicts.

## Algorithm Steps
1. **Fetch Requirements:** Calculate `hours_missing` = `preparation_hours` - `scheduled_hours`.
2. **Find Gaps:** Query Google Calendar for all existing events between `Now` and `Exam Date`. Reverse calculate to find all free slots (e.g., 9 AM to 9 PM daily).
3. **Chunking:** Break large free slots into manageable study chunks (max 2 hours). Add a 30-minute break between chunks to prevent burnout.
4. **Distribution:** Iteratively fill the chunks with study sessions until `hours_missing` is satisfied.
5. **Quality Score:** Calculate a `planner_quality_score` based on how spread out the sessions are versus cramming.
6. **Execution:** Upon user approval, iterate over the chunks and send API calls to Google Calendar. Log identical records to the `study_sessions` database table.
