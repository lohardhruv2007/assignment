import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- CLEAN CENTERED CSS (NO UNDERLINE BAR) ---
st.markdown("""
    <style>
    /* 1. Page Background and Center Alignment */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* Centering the entire content block */
    .main .block-container {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 90vh !important;
        max-width: 800px !important;
        margin: auto !important;
    }

    /* 2. Highlighted Heading (CLEAN - NO BAR) */
    .portal-heading {
        font-size: 65px !important;
        font-weight: 800 !important;
        color: #1b3022 !important;
        text-align: center !important;
        margin-bottom: 40px !important;
        padding-bottom: 10px !important;
        letter-spacing: 1px !important;
    }

    /* 3. Centered Login Card with Perfect Margins */
    .login-box {
        background-color: white !important;
        padding: 50px !important;
        border-radius: 25px !important;
        border: 2px solid #c8d6cc !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08) !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* 4. Large Readable Fonts */
    p, span, label, input {
        font-size: 26px !important;
        color: #2d3e33 !important;
    }

    /* 5. Input Fields (Pastel Green Theme) */
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

    /* 6. Bold Enter Button */
    .stButton>button {
        width: 100% !important;
        height: 85px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 32px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        margin-top: 15px !important;
        transition: 0.3s !important;
    }

    .stButton>button:hover {
        background-color: #3a5142 !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.1) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] * {
        font-size: 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN PAGE ---
if not st.session_state['logged_in']:
    # Clean Heading
    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)
    
    # Perfectly Centered Box
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    user = st.text_input("Username", placeholder="admin", label_visibility="collapsed")
    pwd = st.text_input("Password", type="password", placeholder="hr123", label_visibility="collapsed")
    
    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Screener"
            st.rerun()
        else:
            st.error("Invalid Credentials: Use admin/hr123")
    st.markdown("</div>", unsafe_allow_html=True)

# --- DASHBOARD CONTENT ---
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

    # SCREENER PAGE
    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading" style="font-size:50px !important;">Resume Screening</div>', unsafe_allow_html=True)
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload Batch PDF Resumes (Max 1GB)", type="pdf", accept_multiple_files=True)
        if files and st.button("START AI ANALYSIS"):
            with st.status("Agent analyzing documents...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                s.update(label="Scanning Complete!", state="complete")
            st.session_state['page'] = "Database"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # DATABASE PAGE
    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading" style="font-size:50px !important;">Candidate Pool</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                for _, row in df.iterrows():
                    with st.expander(f"Report: {row['name']} (Score: {row['score']}%)"):
                        st.write(f"**Reasoning:** {row['reason']}")
                        st.progress(row['score'] / 100)
            else: st.info("No records found.")
        except: st.error("Database mismatch. Please use Reset.")

        if st.button("RESET DATABASE"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
