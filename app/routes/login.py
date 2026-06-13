import streamlit as st
from app.database.db import get_connection

def render_login():
    # Add Google Fonts and Custom CSS for premium glassmorphism styling
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
    body {
        font-family: 'Outfit', sans-serif !important;
    }
    .login-container {
        max-width: 450px;
        margin: 80px auto;
        padding: 40px;
        background: rgba(30, 30, 30, 0.75);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }
    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .login-header h2 {
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
        color: #ffffff !important;
        background: linear-gradient(135deg, #ffffff 0%, #a5a5a5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .login-header p {
        color: #888888 !important;
        font-size: 0.95em;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #6200ea 0%, #3700b3 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(98, 0, 234, 0.3) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(98, 0, 234, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Empty columns to center the login card
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="login-header">
            <h2>Smart Timetable AI</h2>
            <p>Sign in or create an account to organize your timetable</p>
        </div>
        """, unsafe_allow_html=True)

        mode = st.radio("Choose Action", ["Login", "Register"], label_visibility="collapsed")
        st.write("")

        if mode == "Login":
            email = st.text_input("Email Address", placeholder="e.g. user@example.com")
            
            if st.button("Access Timetable"):
                if email.strip():
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
                    row = cursor.fetchone()
                    conn.close()

                    if row:
                        user = dict(row)
                        st.session_state.current_user = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("No account found with that email. Please register first.")
                else:
                    st.warning("Please enter your email address.")

        else:  # Register
            new_name = st.text_input("Full Name", placeholder="e.g. John Doe")
            new_email = st.text_input("Email Address", placeholder="e.g. john@example.com")

            if st.button("Create Account"):
                if new_name.strip() and new_email.strip():
                    email_cleaned = new_email.strip().lower()
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    # Check if email already exists
                    cursor.execute("SELECT * FROM users WHERE email = ?", (email_cleaned,))
                    if cursor.fetchone():
                        st.error("An account with this email address already exists.")
                        conn.close()
                    else:
                        try:
                            cursor.execute(
                                "INSERT INTO users (name, email) VALUES (?, ?)",
                                (new_name.strip(), email_cleaned)
                            )
                            conn.commit()
                            
                            # Retrieve the user profile we just created
                            cursor.execute("SELECT * FROM users WHERE email = ?", (email_cleaned,))
                            user = dict(cursor.fetchone())
                            st.session_state.current_user = user
                            conn.close()
                            
                            st.success("Account created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Registration failed: {e}")
                            conn.close()
                else:
                    st.warning("Please fill out both name and email fields.")

        st.markdown('</div>', unsafe_allow_html=True)
