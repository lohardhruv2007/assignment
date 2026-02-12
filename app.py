import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- ULTRA DEEP CSS OVERRIDE ---
st.markdown("""
    <style>
    /* 1. Global Background & Huge Fonts */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    .main {
        background-color: #f3f7f0 !important;
    }

    /* 2. Double Font Size for everything */
    p, span, label, input, button, .stMarkdown {
        font-size: 24px !important;
        font-family: 'Times New Roman', Times, serif !important;
        color: #1b3022 !important;
    }

    h1 { font-size: 60px !important; color: #1b3022 !important; font-weight: bold !important; }
    h2 { font-size: 45px !important; color: #2d3e33 !important; }
    h3 { font-size: 35px !important; }

    /* 3. Input Boxes Fix (Username/Password) */
    div[data-baseweb="input"], input {
        background-color: #e0eadd !important;
        color: #1b3022 !important;
        border: 2px solid #c8d6cc !important;
        font-size: 24px !important;
        border-radius: 10px !important;
    }

    /* 4. Giant Buttons (Enter Dashboard) */
    .stButton>button {
        width: 100% !important;
        height: 80px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 30px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        margin-top: 20px !important;
    }

    .stButton>button:hover {
        background-color: #3a5142 !important;
    }

    /* 5. Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #eef2ef !important;
        border-right: 3px solid #c8d6cc !important;
        width: 400px !important;
    }

    /* 6. File Uploader Navy Blue Fix */
    [data-testid="stFileUploader"] {
        background-color: #e0eadd !important;
        border: 2px dashed #4f6d5a !important;
        border-radius: 15px !important;
    }
    
    [data-testid="stFileUploaderDropzone"] {
        background-color: #e0eadd !important;
    }

    /* 7. Card Styling */
    .card {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 20px !important;
        border: 2px solid #c8d6cc !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN PAGE ---
if not st.session_state['logged_in']:
    _, col2, _ = st.columns([0.5, 2, 0.5])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("💼 Recruiter Portal")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        user = st.text_input("Username (admin)")
        pwd = st.text_input("Password (hr123)", type="password")
        if st.button("ENTER DASHBOARD"):
            if user == "admin" and pwd == "hr123":
                st.session_state['logged_in'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else: st.error("Access Denied: Use admin/hr123")
        st.markdown("</div>", unsafe_allow_html=True)

# --- APP FLOW ---
else:
    with st.sidebar:
        st.markdown("<h1 style='font-size: 40px !important;'>🌿 TalentFlow</h1>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔍 New Screening"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Database"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"): st.session_state['logged_in'] = False; st.rerun()

    # SCREENER PAGE
    if st.session_state['page'] == "Screener":
        st.header("🔍 Intelligent Resume Screening")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload Batch Resumes (Max 1GB)", type="pdf", accept_multiple_files=True)
        if files and st.button("🚀 START AI RANKING"):
            with st.status("Neural Agent Processing...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                s.update(label="Complete!", state="complete")
            st.session_state['page'] = "Database"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # DATABASE PAGE
    elif st.session_state['page'] == "Database":
        st.header("📂 Talent Analytics Pool")
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                
                st.subheader("Decision Breakdown")
                for _, row in df.iterrows():
                    color = "green" if row['score'] >= 70 else "orange" if row['score'] >= 40 else "red"
                    with st.expander(f"Report: {row['name']} (Score: {row['score']}%)"):
                        st.markdown(f"**Status:** :{color}[{row['reason']}]")
                        st.write(f"**Skills Found:** {row['skills']}")
                        st.progress(row['score'] / 100)
            else: st.info("No records found.")
        except: st.error("Database mismatch. Please reset.")

        if st.button("🗑️ RESET DATABASE"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
