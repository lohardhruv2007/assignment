import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

# Page config to remove side margins
st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- THE ERASER CSS (Hides everything you didn't ask for) ---
st.markdown("""
    <style>
    /* 1. COMPLETELY HIDE TOP BAR AND FOOTER */
    [data-testid="stHeader"] {display: none !important;}
    footer {display: none !important;}
    #MainMenu {display: none !important;}
    
    /* 2. Global Background & Perfect Centering */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    .main .block-container {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 100vh !important;
        max-width: 800px !important;
        margin: auto !important;
        padding: 0 !important;
    }

    /* 3. Heading Style */
    .portal-heading {
        font-size: 65px !important;
        font-weight: 800 !important;
        color: #1b3022 !important;
        text-align: center !important;
        margin-bottom: 30px !important;
    }

    /* 4. Login Box Card */
    .login-box {
        background-color: white !important;
        padding: 60px !important;
        border-radius: 25px !important;
        border: 2px solid #c8d6cc !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08) !important;
        width: 100% !important;
    }

    /* 5. Input Fields Styling */
    div[data-baseweb="input"] {
        background-color: #eef2ef !important;
        border: 2px solid #c8d6cc !important;
        border-radius: 12px !important;
        height: 70px !important;
        margin-bottom: 20px !important;
    }

    input {
        font-size: 28px !important;
        text-align: center !important;
    }

    /* 6. Massive Action Button */
    .stButton>button {
        width: 100% !important;
        height: 90px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 34px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        margin-top: 15px !important;
    }

    .stButton>button:hover {
        background-color: #3a5142 !important;
    }
    
    /* Sidebar text adjustment */
    [data-testid="stSidebar"] * {
        font-size: 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN FLOW ---
if not st.session_state['logged_in']:
    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    user = st.text_input("Username", placeholder="admin", label_visibility="collapsed")
    pwd = st.text_input("Password", type="password", placeholder="hr123", label_visibility="collapsed")
    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Screener"
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PROTECTED APP ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#4f6d5a;'>🌿 TalentFlow AI</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔍 New Screening"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Database"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"): 
            st.session_state['logged_in'] = False
            st.rerun()

    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading" style="font-size:50px !important;">Resume Screening</div>', unsafe_allow_html=True)
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("START ANALYSIS"):
            with st.status("Analyzing...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                s.update(label="Scanning Complete!", state="complete")
            st.session_state['page'] = "Database"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading" style="font-size:50px !important;">Candidate Pool</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
            else: st.info("Database is empty.")
        except: st.error("Database error.")
        
        if st.button("RESET DATA"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
