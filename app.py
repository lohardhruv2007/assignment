import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Database Initialization
init_db()

# Sidebar ko hamesha khula rakhne ke liye settings
st.set_page_config(page_title="AI Recruiter Pro", layout="wide", initial_sidebar_state="expanded")

# --- CLEAN TECH CSS (Sidebar ko hamesha dikhane ke liye) ---
st.markdown("""
<style>
    /* Sirf Header aur Footer hide kiye hain, Sidebar ko nahi chheda */
    [data-testid="stHeader"], footer {display: none !important;}
    
    .stApp { background-color: #0e1117 !important; color: #f8fafc; }
    
    .portal-heading {
        font-size: 45px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 20px;
    }

    /* Container adjustments */
    .block-container { padding-top: 1rem !important; }

    /* Input Boxes */
    div[data-baseweb="input"] { background-color: #1e293b !important; border-radius: 8px; }
    input { color: #f8fafc !important; }
    
    /* Buttons */
    .stButton > button {
        width: 100%; background-color: #10b981; color: #000;
        font-weight: 700; border-radius: 8px; height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# Navigation Session State
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Screener"

# --- LOGIN SCREEN ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">System Access</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("User ID", placeholder="admin")
        p = st.text_input("Access Key", type="password", placeholder="hr123")
        if st.button("AUTHENTICATE"):
            if u == "admin" and p == "hr123":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

# --- MAIN DASHBOARD (Login ke baad hamesha dikhegi) ---
else:
    # YE SIDEBAR AB HAMESHA DIKHEGA
    with st.sidebar:
        st.markdown("<h1 style='color:#10b981;'>Admin Panel</h1>", unsafe_allow_html=True)
        st.write("---")
        if st.button("🔍 AI Batch Screener"): 
            st.session_state['page'] = "Screener"
            st.rerun()
        if st.button("📊 Talent Database"): 
            st.session_state['page'] = "Database"
            st.rerun()
        if st.button("🤖 Recruitment Chatbot"): 
            st.session_state['page'] = "Chatbot"
            st.rerun()
        st.write("---")
        if st.button("🚪 Logout"):
            st.session_state['auth'] = False
            st.rerun()

    # Page 1: Screener (PDF Upload)
    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading">Batch AI Analysis</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload Resumes (PDF Only)", type="pdf", accept_multiple_files=True)
        if files and st.button("EXECUTE SCAN"):
            with st.status("AI Analyzing..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
            st.success("Batch Analysis Completed!")

    # Page 2: Database
    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading">Candidate Rankings</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
        st.dataframe(df, use_container_width=True)
        conn.close()

    # Page 3: Chatbot
    elif st.session_state['page'] == "Chatbot":
        st.markdown('<div class="portal-heading">AI Hiring Assistant</div>', unsafe_allow_html=True)
        st.chat_message("assistant").write("Hello! I can help you find the best B.Tech candidates. Ask me anything.")
        prompt = st.chat_input("Ask a question...")
        if prompt:
            st.chat_message("user").write(prompt)
            st.chat_message("assistant").write(f"Analyzing candidates based on: '{prompt}'.")
