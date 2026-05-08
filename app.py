import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# 1. Initialize Database
init_db()

# 2. Page Configuration (Sidebar hamesha open rahegi)
st.set_page_config(
    page_title="TalentFlow AI Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. SAFE CSS (Theme colors, No header hiding to prevent sidebar issues)
st.markdown("""
<style>
    /* Clean Dark Theme without breaking layout */
    .stApp { background-color: #0e1117 !important; color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    .portal-heading {
        font-size: 45px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 25px;
    }
    
    /* Input & Button Styling */
    div[data-baseweb="input"] { background-color: #1e293b !important; border-radius: 8px; }
    input { color: #f8fafc !important; }
    .stButton > button { width: 100%; background-color: #10b981; color: #000; font-weight: 700; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 4. Session States
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#10b981;'>Admin Menu</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Navigation Choice
    choice = st.radio(
        "GO TO:",
        ["AI Batch Screener", "Talent Database", "AI Hiring Assistant"],
        index=0
    )
    
    st.write("---")
    if st.button("🚪 Logout System"):
        st.session_state['auth'] = False
        st.rerun()

# --- 6. AUTHENTICATION PAGE ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">System Access</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Recruiter ID", placeholder="admin")
            p = st.text_input("Security Key", type="password", placeholder="hr123")
            if st.form_submit_button("LOGIN"):
                if u == "admin" and p == "hr123":
                    st.session_state['auth'] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials. Use admin / hr123")
    st.warning("Please login to access the dashboard tools.")

# --- 7. MAIN DASHBOARD CONTENT ---
else:
    # PAGE 1: AI SCREENER
    if choice == "AI Batch Screener":
        st.markdown('<div class="portal-heading">Batch AI Screener</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("RUN AI SCAN"):
            with st.status("AI Agent Analyzing Resumes..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
            st.success(f"Batch Analysis Complete! Processed {len(files)} resumes.")

    # PAGE 2: TALENT DATABASE
    elif choice == "Talent Database":
        st.markdown('<div class="portal-heading">Candidate Rankings</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
            st.dataframe(df, use_container_width=True, height=500)
        except:
            st.info("Database is empty. Please upload resumes in the Screener section.")
        conn.close()

    # PAGE 3: SMART AI CHATBOT
    elif choice == "AI Hiring Assistant":
        st.markdown('<div class="portal-heading">AI Hiring Assistant</div>', unsafe_allow_html=True)
        
        # Display Chat History
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if prompt := st.chat_input("Ask me about hiring or candidate criteria..."):
            st.session_state.chat_history.append({"role
