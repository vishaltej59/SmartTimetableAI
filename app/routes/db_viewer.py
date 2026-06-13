import streamlit as st
import pandas as pd
from app.database.db import get_connection

def render_db_viewer():
    st.subheader("Database Admin & Viewer")
    st.caption("Inspect database tables, review schema details, and execute read-only SQL queries.")

    # High level stats metrics
    try:
        with get_connection() as conn:
            users_cnt = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            assignments_cnt = conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
            exams_cnt = conn.execute("SELECT COUNT(*) FROM exams").fetchone()[0]
            sessions_cnt = conn.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0]
    except Exception as e:
        st.error(f"Failed to fetch database metrics: {e}")
        users_cnt = assignments_cnt = exams_cnt = sessions_cnt = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users", users_cnt)
    col2.metric("Total Assignments", assignments_cnt)
    col3.metric("Total Exams", exams_cnt)
    col4.metric("Study Sessions", sessions_cnt)

    st.divider()

    # Table tabs selection
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 Users", 
        "📝 Assignments", 
        "📅 Exams", 
        "📚 Study Sessions", 
        "🔗 Calendar Syncs", 
        "💻 SQL Console"
    ])

    # 1. Users Tab
    with tab1:
        st.write("### Users Table (`users`)")
        try:
            with get_connection() as conn:
                df_users = pd.read_sql_query("SELECT * FROM users", conn)
            
            if df_users.empty:
                st.info("No records found in users table.")
            else:
                st.dataframe(df_users, use_container_width=True)
                csv = df_users.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Users CSV", csv, "users.csv", "text/csv")
        except Exception as e:
            st.error(f"Error loading users: {e}")

    # 2. Assignments Tab
    with tab2:
        st.write("### Assignments Table (`assignments`)")
        try:
            with get_connection() as conn:
                df_assignments = pd.read_sql_query("SELECT * FROM assignments", conn)
            
            if df_assignments.empty:
                st.info("No records found in assignments table.")
            else:
                # Add filters
                col_p, col_s = st.columns(2)
                prio_filter = col_p.multiselect("Filter Priority", options=df_assignments['priority'].unique(), default=df_assignments['priority'].unique())
                status_filter = col_s.multiselect("Filter Status", options=df_assignments['status'].unique(), default=df_assignments['status'].unique())
                
                filtered_df = df_assignments[
                    df_assignments['priority'].isin(prio_filter) & 
                    df_assignments['status'].isin(status_filter)
                ]
                
                st.dataframe(filtered_df, use_container_width=True)
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Assignments CSV", csv, "assignments.csv", "text/csv")
        except Exception as e:
            st.error(f"Error loading assignments: {e}")

    # 3. Exams Tab
    with tab3:
        st.write("### Exams Table (`exams`)")
        try:
            with get_connection() as conn:
                df_exams = pd.read_sql_query("SELECT * FROM exams", conn)
            
            if df_exams.empty:
                st.info("No records found in exams table.")
            else:
                st.dataframe(df_exams, use_container_width=True)
                csv = df_exams.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Exams CSV", csv, "exams.csv", "text/csv")
        except Exception as e:
            st.error(f"Error loading exams: {e}")

    # 4. Study Sessions Tab
    with tab4:
        st.write("### Study Sessions Table (`study_sessions`)")
        try:
            with get_connection() as conn:
                df_sessions = pd.read_sql_query("SELECT * FROM study_sessions", conn)
            
            if df_sessions.empty:
                st.info("No records found in study_sessions table.")
            else:
                st.dataframe(df_sessions, use_container_width=True)
                csv = df_sessions.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Study Sessions CSV", csv, "study_sessions.csv", "text/csv")
        except Exception as e:
            st.error(f"Error loading study sessions: {e}")

    # 5. Calendar Syncs Tab
    with tab5:
        st.write("### Calendar Syncs Table (`scheduled_sessions`)")
        try:
            with get_connection() as conn:
                df_syncs = pd.read_sql_query("SELECT * FROM scheduled_sessions", conn)
            
            if df_syncs.empty:
                st.info("No records found in scheduled_sessions table.")
            else:
                st.dataframe(df_syncs, use_container_width=True)
                csv = df_syncs.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Calendar Syncs CSV", csv, "scheduled_sessions.csv", "text/csv")
        except Exception as e:
            st.error(f"Error loading scheduled sessions: {e}")

    # 6. SQL Console Tab
    with tab6:
        st.write("### SQL Execution Console")
        st.caption("Write and execute database queries directly. Only read-only `SELECT` queries are permitted for safety.")
        
        query = st.text_area("SQL Query", value="SELECT * FROM users LIMIT 10;", height=100)
        
        if st.button("Execute Query", type="primary"):
            if not query.strip():
                st.warning("Please enter a query.")
            elif not query.strip().lower().startswith("select"):
                st.error("Operation Blocked: Only read-only `SELECT` queries are allowed to protect database integrity.")
            else:
                try:
                    with get_connection() as conn:
                        df_result = pd.read_sql_query(query, conn)
                    
                    st.success("Query executed successfully!")
                    st.dataframe(df_result, use_container_width=True)
                except Exception as e:
                    st.error(f"SQL Execution Error: {e}")
