import streamlit as st
import pandas as pd
import sqlite3
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Step 1: Initialize Database
init_db()

st.set_page_config(page_title="TalentFlow AI | Enterprise", page_icon="💼", layout="wide")

# Session States for Flow
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"

# --- 1. LOGIN PAGE ---
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

# --- 2. SCREENER PAGE ---
elif st.session_state['page'] == "Screener":
    st.sidebar.title("TalentFlow AI")
    if st.sidebar.button("📊 View Database"):
        st.session_state['page'] = "Database"
        st.rerun()
    
    st.header("🔍 AI Resume Screener")
    st.write("Upload resumes to see Selection/Rejection reasons.")
    
    files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
    if files and st.button("Analyze & Rank"):
        with st.spinner("AI is thinking..."):
            for f in files:
                text = extract_text_from_pdf(f)
                res = analyze_resume(text)
                # 'reason' field bhi save hoga
                save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
        st.success("Analysis Complete!")
        st.session_state['page'] = "Database"
        st.rerun()

# --- 3. DATABASE PAGE (Reasoning Insights) ---
elif st.session_state['page'] == "Database":
    st.sidebar.title("TalentFlow AI")
    if st.sidebar.button("🔍 New Screening"):
        st.session_state['page'] = "Screener"
        st.rerun()

    st.header("📂 Candidate Pool & Intelligent Insights")
    conn = sqlite3.connect('candidates.db')
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    
    if not df.empty:
        # Ranking based on score
        st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
        
        st.subheader("Automated Decision Feedback")
        for index, row in df.iterrows():
            with st.expander(f"Analysis for {row['name']}"):
                st.write(f"**Final Status:** {row['reason']}")
                st.progress(row['score'] / 100)
    else:
        st.info("No records found.")
    
    if st.button("🗑️ Clear Database"):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM candidates")
        conn.commit()
        st.rerun()
    conn.close()
