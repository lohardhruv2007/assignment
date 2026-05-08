import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Step 1: Secure Initialization
init_db()

st.set_page_config(page_title="TalentFlow AI Command Center", layout="wide")

# --- PRO DARK TECH THEME (Zero Bars) ---
st.markdown("""
<style>
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    .stApp { background-color: #0e1117 !important; font-family: 'Inter', sans-serif !important; }
    
    .main .block-container {
        padding-top: 2rem !important;
        max-width: 1200px !important;
        margin: auto !important;
    }

    .portal-heading {
        font-size: 45px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 20px;
    }

    .glass-card {
        background-color: #161e2e; padding: 30px; border-radius: 15px;
        border: 1px solid #1f2937; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Input & Sidebar Styling */
    div[data-baseweb="input"] { background-color: #1e293b !important; border-radius: 8px; }
    input { color: #f8fafc !important; }
    .stButton > button {
        width: 100%; background-color: #10b981; color: #000;
        font-weight: 700; border-radius: 8px; height: 50px;
    }
</style>
""", unsafe_allow_html=True)

# Session States
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"
if 'messages' not in st.session_state: st.session_state['messages'] = []

# --- 1. LOGIN SYSTEM ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">AI Recruiter Access</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        u = st.text_input("Recruiter ID")
        p = st.text_input("Security Key (hr123)", type="password")
        if st.button("AUTHENTICATE"):
            if u == "admin" and p == "hr123":
                st.session_state['auth'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else:
                st.error("Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. MAIN DASHBOARD ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#10b981;'>Command Center</h2>", unsafe_allow_html=True)
        if st.button("🔍 AI Batch Screener"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Database"): st.session_state['page'] = "Database"; st.rerun()
        if st.button("🤖 AI Recruitment Chatbot"): st.session_state['page'] = "Chatbot"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout"): 
            st.session_state['auth'] = False
            st.rerun()

    # --- PAGE: SCREENER (PDF Uploader) ---
    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading">Batch AI Analysis</div>', unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("START SCANNING"):
            with st.status("AI Agent analyzing..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
            st.success("Batch Analysis Complete.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PAGE: DATABASE ---
    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading">Shortlisted Talent</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
        st.dataframe(df, use_container_width=True)
        conn.close()

    # --- PAGE: AI CHATBOT (Tera AI Chatbot bhai) ---
    elif st.session_state['page'] == "Chatbot":
        st.markdown('<div class="portal-heading">HR AI Assistant</div>', unsafe_allow_html=True)
        
        # Chat History Display
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about candidates or hiring..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Bot Response Logic (Mock AI for Demo)
            with st.chat_message("assistant"):
                response = f"Analyzing database for: '{prompt}'. Based on B.Tech criteria, I recommend checking candidates with scores > 75%."
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
