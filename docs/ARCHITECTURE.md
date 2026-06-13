# System Architecture

## Overview
Smart Timetable AI uses a standard MVC / Service-Oriented pattern built entirely in Python using Streamlit for the presentation layer.

## Layers
1. **Presentation (Routes)**
   - `app/routes/`: Streamlit UI components mapped to sidebar navigation.
2. **Business Logic (Services)**
   - `app/services/`: Core logic decoupled from the UI. Handlers for DB operations, Google API, algorithms, and AI connection.
3. **Data Access (Database)**
   - `app/database/db.py`: SQLite connection singleton and raw SQL queries.
4. **Tools & Integrations**
   - `app/tools/agent_tools.py`: JSON schemas mapping Python functions to Groq LLM tool calls.
   - Google Calendar API: Handled via `auth_service.py` and `calendar_service.py`.

## Flow
User Action -> Route -> Service -> Database / External API -> Update UI State -> Streamlit Rerun.
