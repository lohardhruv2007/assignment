import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize
init_db()

st.set_page_config(page_title="TalentFlow AI", page_icon="💼", layout="wide")

# Simple Flow Control
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"

# --- LOGIN ---
if not st.session_state['logged_in']:
    st.title("💼 Recruiter Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Screener"
            st.rerun()
        else:
            st.error("Access Denied (admin/hr123)")

# --- LOGGED IN ---
else:
    st.sidebar.title("TalentFlow AI")
    if st.sidebar.button("🔍 New Screening"):
        st.session_state['page'] = "Screener"
        st.rerun()
    if st.sidebar.button("📂 View Database"):
        st.session_state['page'] = "Database"
        st.rerun()
    if st.sidebar.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # SCREENER PAGE
    if st.session_state['page'] == "Screener":
        st.header("🔍 Intelligent Resume Screening")
        st.info("Supported: Text PDFs & Scanned Images (OCR Mode Active)")
        
        files = st.file_uploader("Upload Resumes (Max 1GB)", type="pdf", accept_multiple_files=True)
        if files and st.button("Analyze & Generate Reasons"):
            with st.status("AI Agent is reading resumes..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
            st.success("Analysis Complete!")
            st.session_state['page'] = "Database"
            st.rerun()

    # DATABASE PAGE
    elif st.session_state['page'] == "Database":
        st.header("📂 Talent Pool Insights")
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                
                st.subheader("Automated Feedback")
                for _, row in df.iterrows():
                    with st.expander(f"Decision for {row['name']}"):
                        st.write(f"**Reasoning:** {row['reason']}")
                        st.progress(row['score'] / 100)
            else:
                st.info("Database is empty. Please upload resumes.")
        except Exception:
            st.error("Database Schema Mismatch! Please click 'Reset Database' below.")

        if st.button("🗑️ Reset Database (Fix Errors)"):
            conn.close()
            if os.path.exists('candidates.db'):
                os.remove('candidates.db')
            st.rerun()
        conn.close()
