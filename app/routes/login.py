import streamlit as st
from app.database.db import get_connection

def render_login():
    # CSS styled to build a premium split-screen card with capsule buttons and abstract shapes
    css = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"><style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #4f46e5, #6C3BFF, #a855f7) !important;
    }
    
    /* Layout wrapping for horizontal block columns */
    div[data-testid="stHorizontalBlock"] {
        background: #FFFFFF !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
        overflow: hidden !important;
        max-width: 960px !important;
        margin: 60px auto !important;
        gap: 0px !important;
        border: none !important;
    }
    
    /* Left column visual panel */
    div[data-testid="stColumn"]:has(.left-container) {
        background: linear-gradient(135deg, #6C3BFF, #8b5cf6, #ec4899, #ff7e5f) !important;
        padding: 48px !important;
        color: #FFFFFF !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        min-height: 580px !important;
        overflow: hidden !important;
    }
    
    /* Right column input fields panel */
    div[data-testid="stColumn"]:has(.left-container) + div[data-testid="stColumn"] {
        background: #FFFFFF !important;
        padding: 48px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        min-height: 580px !important;
    }
    
    /* Hide native Streamlit border wrappers */
    div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
    }
    
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Left container visuals styling */
    .left-container {
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }
    .logo-area {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 24px;
    }
    .left-logo-icon {
        font-size: 24px;
        background: rgba(255, 255, 255, 0.2);
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .left-logo-text {
        font-weight: 800;
        font-size: 1.25em;
        letter-spacing: -0.5px;
    }
    .left-hero h1 {
        font-size: 2.25em !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        margin: 0 0 14px 0 !important;
        color: #FFFFFF !important;
        letter-spacing: -1px;
    }
    .left-hero p {
        font-size: 0.95em !important;
        color: rgba(255, 255, 255, 0.85) !important;
        line-height: 1.5 !important;
        margin: 0 !important;
    }
    .bullets-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 28px;
    }
    .bullet-item {
        font-weight: 600;
        font-size: 0.95em;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Abstract capsule graphic shapes */
    .abstract-shape {
        position: absolute;
        border-radius: 50px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0));
        z-index: 1;
        transform: rotate(-35deg);
    }
    .shape-1 {
        width: 160px;
        height: 45px;
        bottom: 10px;
        left: -40px;
    }
    .shape-2 {
        width: 220px;
        height: 60px;
        bottom: -30px;
        left: 60px;
        background: linear-gradient(135deg, rgba(255, 126, 95, 0.35), rgba(255, 126, 95, 0));
    }
    .shape-3 {
        width: 140px;
        height: 35px;
        bottom: 80px;
        right: -30px;
    }
    
    /* Styled Input Fields matching user image */
    div[data-testid="stTextInput"] input {
        background-color: #F1EFFE !important;
        border: 1px solid #E2DDFB !important;
        color: #1E293B !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #6C3BFF !important;
        box-shadow: 0 0 0 1px #6C3BFF !important;
    }
    div[data-testid="stTextInput"] label p {
        font-weight: 600 !important;
        color: #475569 !important;
    }
    
    /* Custom segmented tab switch control */
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        background: #F1F5F9 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        margin-bottom: 24px !important;
        gap: 0px !important;
        width: 100% !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[role="radiogroup"] label {
        flex: 1 !important;
        width: 50% !important;
        max-width: 50% !important;
        text-align: center !important;
        justify-content: center !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        border: none !important;
        margin: 0 !important;
        background: transparent !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        height: 36px !important;
    }
    div[role="radiogroup"] label:hover {
        background: rgba(0, 0, 0, 0.02) !important;
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background: #6C3BFF !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    div[role="radiogroup"] label p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        color: #64748B !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
    }
    div[role="radiogroup"] label[data-checked="true"] p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    div[role="radiogroup"] label input {
        display: none !important;
    }
    
    /* Capsule sign in buttons styling */
    .stButton>button {
        width: 100% !important;
        background: linear-gradient(135deg, #6C3BFF, #8b5cf6, #ec4899) !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        border: none !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 10px rgba(108, 59, 255, 0.25) !important;
    }
    .stButton>button:hover {
        opacity: 0.95 !important;
        transform: translateY(-0.5px) !important;
        box-shadow: 0 6px 15px rgba(108, 59, 255, 0.35) !important;
    }
    
    /* Social Buttons styling overrides */
    .stLinkButton > a {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #1E293B !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        text-align: center !important;
        font-size: 0.9em !important;
        transition: all 0.2s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    .stLinkButton > a:hover {
        background: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #1E293B !important;
        transform: translateY(-0.5px) !important;
    }
    .or-divider {
        display: flex;
        align-items: center;
        text-align: center;
        color: #94A3B8;
        font-size: 0.8em;
        font-weight: 700;
        margin: 24px 0 16px 0;
    }
    .or-divider::before, .or-divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #E2E8F0;
    }
    .or-divider:not(:empty)::before {
        margin-right: .8em;
    }
    .or-divider:not(:empty)::after {
        margin-left: .8em;
    }
    </style>"""
    st.markdown(css, unsafe_allow_html=True)

    # Main split screen columns
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown("""
        <div class="left-container">
            <div class="logo-area">
                <div class="left-logo-icon">📅</div>
                <div class="left-logo-text">Smart Timetable AI</div>
            </div>
            <div class="left-hero">
                <h1>Plan Smarter.<br>Study Better.</h1>
                <p>AI-powered academic planning, scheduling, reminders, and exam preparation.</p>
            </div>
            <div class="bullets-list">
                <div class="bullet-item">✓ Smart Scheduling</div>
                <div class="bullet-item">✓ Google Calendar Sync</div>
                <div class="bullet-item">✓ Exam Planning</div>
                <div class="bullet-item">✓ AI Study Assistant</div>
            </div>
            <!-- Abstract capsule graphic shapes -->
            <div class="abstract-shape shape-1"></div>
            <div class="abstract-shape shape-2"></div>
            <div class="abstract-shape shape-3"></div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        mode = st.radio("Mode Selection", ["Login", "Register"], label_visibility="collapsed")
        st.write("")

        if mode == "Login":
            email = st.text_input("Email Address", key="login_email", placeholder="e.g. user@example.com")
            password = st.text_input("Password", key="login_pwd", type="password", placeholder="••••••••")
            
            # Remember Me and Forgot Password in columns
            c_rem, c_forgot = st.columns([1.1, 0.9])
            with c_rem:
                st.checkbox("Remember Me", value=True, key="login_remember")
            with c_forgot:
                st.markdown('<div style="text-align: right; margin-top: 4px;"><a href="#" style="color: #6C3BFF; text-decoration: none; font-size: 0.85em; font-weight: 600;">Forgot Password?</a></div>', unsafe_allow_html=True)
            
            st.write("")
            if st.button("Sign In", key="login_submit", type="primary", use_container_width=True):
                if email.strip() and password.strip():
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
                    st.warning("Please fill in both email and password fields.")

        else: # Register
            new_name = st.text_input("Full Name", key="register_name", placeholder="e.g. John Doe")
            new_email = st.text_input("Email Address", key="register_email", placeholder="e.g. john@example.com")
            new_pwd = st.text_input("Password", key="register_pwd", type="password", placeholder="••••••••")
            confirm_pwd = st.text_input("Confirm Password", key="register_confirm_pwd", type="password", placeholder="••••••••")
            
            # Real-time Password Strength Indicator
            if new_pwd:
                strength = "Weak"
                strength_color = "#EF4444"
                strength_pct = "33%"
                if len(new_pwd) >= 6:
                    strength = "Medium"
                    strength_color = "#F59E0B"
                    strength_pct = "66%"
                    if len(new_pwd) >= 8 and any(c in "!@#$%^&*()_+-=" for c in new_pwd):
                        strength = "Strong"
                        strength_color = "#10B981"
                        strength_pct = "100%"
                st.markdown(f"""
                <div style="margin-top: 4px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8em; font-weight: 600; color: #64748B; margin-bottom: 4px;">
                        <span>Password Strength:</span>
                        <span style="color: {strength_color};">{strength}</span>
                    </div>
                    <div style="background: #E2E8F0; height: 4px; border-radius: 2px; width: 100%;">
                        <div style="background: {strength_color}; height: 100%; border-radius: 2px; width: {strength_pct}; transition: width 0.3s ease;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            terms = st.checkbox("I agree to the Terms & Conditions", key="register_terms")
            
            st.write("")
            if st.button("Create Account", key="register_submit", type="primary", use_container_width=True):
                if new_name.strip() and new_email.strip() and new_pwd.strip() and confirm_pwd.strip():
                    if new_pwd != confirm_pwd:
                        st.error("Passwords do not match.")
                    elif not terms:
                        st.error("Please agree to the Terms & Conditions.")
                    else:
                        email_cleaned = new_email.strip().lower()
                        conn = get_connection()
                        cursor = conn.cursor()
                        
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
                    st.warning("Please fill out all input fields.")

        google_auth_url = "#"
        try:
            from app.services.auth_service import get_google_flow
            flow = get_google_flow("login")
            flow.code_verifier = "smart_timetable_ai_agent_secret_code_verifier_value_for_pkce_auth_flow_123456789"
            google_auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent',
                state='login'
            )
        except Exception as e:
            pass

        st.markdown('<div class="or-divider">OR</div>', unsafe_allow_html=True)
        
        # Social sign-in links
        c_google, c_msft = st.columns(2)
        with c_google:
            st.link_button(" Google", url=google_auth_url, use_container_width=True, icon="🌐")
        with c_msft:
            st.link_button(" Microsoft", url="#", use_container_width=True, icon="💻")
