import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- THE ABSOLUTE ERASER (Aggressive CSS Reset) ---
st.markdown("""
    <style>
    /* 1. HIDE EVERYTHING: Header, Footer, Main Menu, and Gaps */
    [data-testid="stHeader"], footer, #MainMenu {
        display: none !important;
    }

    /* 2. FORCE TOTAL BACKGROUND (No White Gaps) */
    .stApp {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* 3. KILL TOP PADDING & CENTER CONTENT */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        height: 100vh !important;
        max-width: 100% !important;
    }

    /* 4. RECRUITER PORTAL HEADING */
    .portal-heading {
        font-size: 70px !important;
        font-weight: 800 !important;
        color: #1b3022 !important;
        text-align: center !important;
        margin-bottom: 30px !important;
    }

    /* 5. INPUT BOXES FIX (Dark color hatakar pastel green) */
    div[data-baseweb="input"], [data-testid="stTextInput"] > div {
        background-color: #eef2ef !important;
        border: 2px solid #c8d6cc !important;
        border-radius: 12px !important;
        color: #1b3022 !important;
        height: 65px !important;
    }

    input {
        background-color: transparent !important;
        font-size: 26px !important;
        text-align: center !important;
        color: #1b3022 !important;
    }

    /* 6. GIANT ENTER BUTTON */
    .stButton > button {
        width: 100% !important;
        height: 80px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 32px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        margin-top: 20px !important;
    }

    /* 7. LOGIN BOX CARD */
    .login-box {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 25px !important;
        border: 2px solid #c8d6cc !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        width: 550px !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    /* Sidebar huge text fix */
    [data-testid="stSidebar"] * {
        font-size: 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"

# --- LOGIN FLOW ---
if not st.session_state['logged_in']:
    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    user = st.text_input("User", placeholder="admin", label_visibility="collapsed")
    pwd = st.text_input("Pass", type="password", placeholder="hr123", label_visibility="collapsed")
    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Screener"
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PROTECTED APP CONTENT ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#4f6d5a;'>🌿 TalentFlow AI</h2>", unsafe_allow_html=True)
        if st.button("🔍 New Screening"): 
            st.session_state['page'] = "Screener"
            st.rerun()
        if st.button("📊 Talent Database"): 
            st.session_state['page'] = "Database"
            st.rerun()
        if st.button("🚪 Logout"): 
            st.session_state['logged_in'] = False
            st.rerun()

    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading" style="font-size:50px !important;">Resume Screening</div>', unsafe_allow_html=True)
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("START ANALYSIS"):
            with st.status("Analyzing..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
            st.session_state['page'] = "Database"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading" style="font-size:50px !important;">Candidate Pool</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        if not df.empty:
            st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
        if st.button("RESET DATABASE"):
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
