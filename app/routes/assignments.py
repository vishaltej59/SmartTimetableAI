import streamlit as st
from app.services.assignment_service import (
    add_assignment,
    get_assignments,
    complete_assignment,
    delete_assignment,
)
from datetime import datetime

def render_assignments():
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h2 style="font-size: 2em; font-weight: 800; color: #0F172A; letter-spacing: -1px; margin-bottom: 4px;">Assignments Checklist</h2>
        <p style="color: #475569; font-size: 1.05em; margin: 0;">Track, prioritize, and manage homework deadlines and project milestones.</p>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.current_user["id"]

    # Expandable "Add Assignment" drawer
    with st.expander("➕ Create New Assignment"):
        with st.form("assignment_form"):
            title = st.text_input("Assignment Title", placeholder="e.g. Math Problem Set 3")
            due_date = st.date_input("Due Date", datetime.now().date())
            estimated_hours = st.number_input(
                "Estimated Hours", min_value=0.5, value=1.0, step=0.5
            )
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])

            submitted = st.form_submit_button("Add Assignment", type="primary")

            if submitted:
                if title.strip():
                    add_assignment(
                        user_id, title, str(due_date), priority, estimated_hours
                    )
                    st.success("Assignment added successfully.")
                    st.rerun()
                else:
                    st.error("Please enter assignment title.")

    st.write("")
    st.write("### 🔍 Filter & Search Tasks")
    
    # Grid of Search, Filters, and Sorting
    c_search, c_pri, c_stat, c_sort = st.columns([1.5, 1.0, 1.0, 1.2], gap="small")
    
    with c_search:
        search_query = st.text_input("Search tasks", placeholder="Search by title...", label_visibility="collapsed")
    with c_pri:
        priority_filter = st.selectbox("Priority", ["All Priorities", "High", "Medium", "Low"], label_visibility="collapsed")
    with c_stat:
        status_filter = st.selectbox("Status", ["All Statuses", "Pending", "Completed"], label_visibility="collapsed")
    with c_sort:
        sort_by = st.selectbox("Sort order", ["Due Date: Soonest", "Due Date: Latest", "Title: A-Z", "Title: Z-A"], label_visibility="collapsed")

    # Load list of assignments
    assignments = get_assignments(user_id)
    
    # Filter
    filtered = []
    for a in assignments:
        if search_query.strip() and search_query.strip().lower() not in a["title"].lower():
            continue
        if priority_filter != "All Priorities" and a["priority"] != priority_filter:
            continue
        if status_filter != "All Statuses" and a["status"] != status_filter:
            continue
        filtered.append(a)

    # Sort
    if "Due Date" in sort_by:
        reverse_sort = "Latest" in sort_by
        def get_due_date(x):
            try:
                return datetime.strptime(x["due_date"], "%Y-%m-%d").date()
            except Exception:
                return datetime.max.date()
        filtered.sort(key=get_due_date, reverse=reverse_sort)
    else:
        reverse_sort = "Z-A" in sort_by
        filtered.sort(key=lambda x: x["title"].lower(), reverse=reverse_sort)

    st.write("")
    
    # Custom assignment cards style
    st.markdown("""
    <style>
    .task-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .task-details {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .task-title {
        font-weight: 700;
        color: #0F172A;
        font-size: 1.05em;
        margin: 0;
    }
    .task-meta {
        font-size: 0.85em;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .badge {
        font-size: 0.75em;
        font-weight: 700;
        padding: 2.5px 8px;
        border-radius: 6px;
    }
    .badge-high { background: #FEF2F2; color: #EF4444; }
    .badge-medium { background: #FFF7ED; color: #F97316; }
    .badge-low { background: #F0FDF4; color: #10B981; }
    .badge-pending { background: #F1F5F9; color: #475569; }
    .badge-completed { background: #E6FBF3; color: #10B981; }
    </style>
    """, unsafe_allow_html=True)

    if not filtered:
        st.info("No assignments match your search/filters.")
    else:
        for item in filtered:
            pri_class = f"badge-{item['priority'].lower()}"
            stat_class = f"badge-{item['status'].lower()}"
            
            # Format UI HTML card
            st.markdown(f"""
            <div class="task-card">
                <div class="task-details">
                    <h4 class="task-title">{item['title']}</h4>
                    <div class="task-meta">
                        <span>Due: <b>{item['due_date']}</b></span>
                        <span>•</span>
                        <span>Est: <b>{item['estimated_hours']}h</b></span>
                        <span class="badge {pri_class}">{item['priority']}</span>
                        <span class="badge {stat_class}">{item['status']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons below or side-by-side using columns for Streamlit interaction
            col_act1, col_act2, col_spacer = st.columns([1, 1, 5])
            with col_act1:
                if item["status"] != "Completed":
                    if st.button("Complete", key=f"complete_{item['id']}", use_container_width=True):
                        complete_assignment(item["id"])
                        st.rerun()
            with col_act2:
                if st.button("Delete", key=f"delete_{item['id']}", use_container_width=True):
                    delete_assignment(item["id"])
                    st.rerun()
            st.write("")

