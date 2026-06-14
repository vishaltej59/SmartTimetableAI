# Smart Timetable AI Agent

Smart Timetable AI is an intelligent study planner and calendar manager built with Python, Streamlit, and Gemini's LLM engine. It acts as an autonomous AI assistant that helps students and professionals generate dynamic study plans, track their study progress, detect calendar conflicts, and interact with their schedule via natural language.

---

## 🎯 Features

- **Dynamic Study Planner**: Automatically generate chunked study sessions mapping exactly to your free Google Calendar slots.
- **Study Progress Tracking**: Monitor planned vs. completed hours with interactive progress bars, readiness scores, and visual analytics.
- **AI Scheduling Assistant**: Natural language chat interface powered by the Gemini 2.5 Flash API (with dynamic quota fallback to Gemini Flash Latest) and native tool calling. Ask it to schedule a block, query your progress, or find free time.
- **Google Calendar Sync**: Full read/write integration. Event conflicts are automatically detected and avoided.
- **Multi-User isolation**: Secure database and calendar isolation. OAuth 2.0 flows, Google API client tokens, and database models are strictly segregated per user.
- **Task & Exam Management**: Track assignment deadlines and exam dates seamlessly.
- **Smart Alerts**: Dashboard warnings for upcoming deadlines and off-track progress.

---

## 🏗 Architecture

- **Frontend**: Streamlit (Python)
- **Database**: SQLite (Local database storing users, assignments, exams, and progress)
- **AI Brain**: Gemini 2.5 Flash API (with native tool-calling for function execution and rate-limiting resilience)
- **Integrations**: Google Calendar API (OAuth 2.0)

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd "Smart Timetable AI"
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Calendar Credentials:**
   - Go to the Google Cloud Console.
   - Create an OAuth 2.0 Client ID (Web Application).
   - Configure the Redirect URI (e.g., `http://localhost:8501`).
   - Download the client credentials JSON file and save it in the `credentials/` folder named `credentials.json`.

5. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your API keys and Google Client details:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   REDIRECT_URI=http://localhost:8501
   ```

---

## 💻 Usage Guide

Start the Streamlit application:
```bash
streamlit run main.py
```

**Navigation Flow:**
1. **Login page:** Authenticate securely using Google OAuth login.
2. **Assignments/Exams:** Input your upcoming academic deadlines.
3. **Study Planner:** Select an exam and hit 'Generate Plan'. The system maps required hours to free slots in your Google Calendar.
4. **Study Progress:** As you study, mark sessions as 'Done' to increment your Readiness Score and update your analytics charts.
5. **AI Assistant:** Chat naturally (e.g., "Am I ready for my DBMS exam?") and let the agent query the database and calendar for you.

---

## 🔮 Future Improvements
- Migration to PostgreSQL database for production deployments.
- Predictive Analytics for AI-driven exam readiness predictions.
- PDF Syllabus parsing via RAG to auto-populate study plans.

