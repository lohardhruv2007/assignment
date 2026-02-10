import streamlit as st
import pandas as pd
import sqlite3
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

init_db()
st.set_page_config(page_title="TalentFlow AI", page_icon="💼", layout="wide")

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
            st.error("Invalid Credentials (admin/hr123)")

# --- SCREENER ---
elif st.session_state['page'] == "Screener":
    st.header("🔍 Step 1: Smart Resume Screening")
    files = st.file_uploader("Upload Resumes (Max 1GB)", type="pdf", accept_multiple_files=True)
    if files and st.button("Process & Save"):
        with st.spinner("Analyzing with OCR..."):
            for f in files:
                text = extract_text_from_pdf(f)
                res = analyze_resume(text)
                save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]))
        st.session_state['page'] = "Database"
        st.rerun()

# --- DATABASE & DELETE ---
elif st.session_state['page'] == "Database":
    st.header("📂 Candidate Pool & Management")
    conn = sqlite3.connect('candidates.db')
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
    
    if st.button("🗑️ Clear All Data"):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM candidates")
        conn.commit()
        st.rerun()
    if st.button("⬅️ Back to Screener"):
        st.session_state['page'] = "Screener"
        st.rerun()
    conn.close()
