import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Step 1: Initialize Database
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🚀", layout="wide")

# --- CUSTOM CSS (Error Fixed here) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #1b5e20; }
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid #e0e0e0;
    }
    h1, h2, h3 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True) # FIXED: changed stdio to html

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN PAGE ---
if not st.session_state['logged_in']:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.title("Recruiter Portal")
        st.write("Sign in to access AI Screening tools")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Authorize Access"):
            if user == "admin" and pwd == "hr123":
                st.session_state['logged_in'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else: st.error("Access Denied: Incorrect Credentials")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PROTECTED APP CONTENT ---
else:
    with st.sidebar:
        st.title("🚀 TalentFlow AI")
        st.markdown("---")
        if st.sidebar.button("🔍 Resume Screener"): st.session_state['page'] = "Screener"; st.rerun()
        if st.sidebar.button("📊 Insight Dashboard"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("---")
        if st.sidebar.button("Logout"): 
            st.session_state['logged_in'] = False
            st.rerun()

    # SCREENER PAGE
    if st.session_state['page'] == "Screener":
        st.header("🔍 Intelligent Screening Agent")
        st.write("Upload PDF resumes for high-speed AI analysis and ranking.")
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload Batch (PDF only)", type="pdf", accept_multiple_files=True)
        if files and st.button("⚡ Start Neural Ranking"):
            with st.status("Analyzing content and extracting features...", expanded=True) as status:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                status.update(label="Scanning Complete!", state="complete", expanded=False)
            st.session_state['page'] = "Database"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # DATABASE PAGE
    elif st.session_state['page'] == "Database":
        st.header("📊 Talent Analytics Dashboard")
        
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                # Top Level Analytics
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Candidates", len(df))
                c2.metric("Avg Quality Score", f"{int(df['score'].mean())}%")
                top_name = df.sort_values(by="score", ascending=False).iloc[0]['name']
                c3.metric("Top Talent", top_name)

                st.markdown("---")
                # Data Table
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                
                # Decision Insights
                st.subheader("🤖 AI Decision Logs")
                for _, row in df.iterrows():
                    # Color coding for reasons
                    color = "green" if row['score'] >= 70 else "orange" if row['score'] >= 40 else "red"
                    with st.expander(f"Report: {row['name']} (Score: {row['score']}%)"):
                        st.markdown(f"**AI Status:** :{color}[{row['reason']}]")
                        st.write(f"**Found Skills:** {row['skills']}")
                        st.progress(row['score'] / 100)
            else:
                st.info("No candidates analyzed yet. Go to 'Resume Screener' to start.")
        except Exception:
            st.error("Database Schema Error. Please reset below.")

        st.markdown("---")
        if st.button("🗑️ Reset Application Data"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
