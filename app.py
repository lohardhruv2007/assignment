import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- THE ABSOLUTE CLEAN UI (Headers Fixed & Centered) ---
st.markdown("""
<style>
    /* 1. Hide Streamlit Default Bars */
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}

    /* 2. Page Background */
    .stApp {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* 3. Global Centering & Margin Fix */
    .main .block-container {
        padding-top: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        height: 100vh !important;
        max-width: 900px !important;
        margin: auto !important;
    }

    /* 4. Portal Heading */
    .portal-heading {
        font-size: 70px !important;
        font-weight: 800 !important;
        color: #1b3022 !important;
        text-align: center !important;
        margin-bottom: 30px !important;
    }

    /* 5. Input Labels Restored */
    label {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #1b3022 !important;
        margin-bottom: 10px !important;
        display: block !important;
    }

    /* 6. Input Box Styling (No Navy Blue) */
    div[data-baseweb="input"] {
        background-color: #eef2ef !important;
        border: 2px solid #c8d6cc !important;
        border-radius: 12px !important;
        height: 70px !important;
    }

    input {
        font-size: 26px !important;
        text-align: center !important;
        color: #1b3022 !important;
    }

    /* 7. Centered Login Card */
    .login-box {
        background-color: white !important;
        padding: 50px !important;
        border-radius: 25px !important;
        border: 2px solid #c8d6cc !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08) !important;
        width: 100% !important;
    }

    /* 8. Big Action Button */
    .stButton > button {
        width: 100% !important;
        height: 85px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 32px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        margin-top: 25px !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #3a5142 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"

# --- UI FLOW ---
if not st.session_state['logged_in']:
    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    user = st.text_input("Username", placeholder="admin")
    pwd = st.text_input("Password", type="password", placeholder="hr123")
    
    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Screener"
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown("<h2 style='color:#4f6d5a;'>🌿 TalentFlow AI</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔍 New Screening"): 
            st.session_state['page'] = "Screener"
            st.rerun()
        if st.button("📊 Talent Database"): 
            st.session_state['page'] = "Database"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout"): 
            st.session_state['logged_in'] = False
            st.rerun()

    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading" style="font-size:50px !important;">Resume Screening</div>', unsafe_allow_html=True)
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload Resumes (Max 1GB PDF)", type="pdf", accept_multiple_files=True)
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
        if st.button("RESET DATA"):
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
