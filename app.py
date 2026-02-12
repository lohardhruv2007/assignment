import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🚀", layout="wide")

# --- CUSTOM CSS FOR UI ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #0056b3; border: none; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_stdio=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN PAGE ---
if not st.session_state['logged_in']:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.title("💼 Recruiter Login")
        st.write("Welcome to TalentFlow AI Enterprise Edition")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Secure Login"):
            if user == "admin" and pwd == "hr123":
                st.session_state['logged_in'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else: st.error("Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)

# --- APP FLOW ---
else:
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
        st.title("TalentFlow Pro")
        st.markdown("---")
        if st.button("🔍 New Screening"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Database"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout"): st.session_state['logged_in'] = False; st.rerun()

    # SCREENER PAGE
    if st.session_state['page'] == "Screener":
        st.header("🔍 Intelligent Talent Screening")
        st.write("Upload candidate resumes for instant AI ranking and reasoning.")
        
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            files = st.file_uploader("Drop PDF files here (Max 1GB)", type="pdf", accept_multiple_files=True)
            if files and st.button("🚀 Start AI Analysis"):
                with st.status("Reading resumes & performing OCR...", expanded=True) as status:
                    for f in files:
                        st.write(f"Processing: {f.name}...")
                        text = extract_text_from_pdf(f)
                        res = analyze_resume(text)
                        save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                    status.update(label="Analysis Complete!", state="complete", expanded=False)
                st.session_state['page'] = "Database"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # DATABASE PAGE
    elif st.session_state['page'] == "Database":
        st.header("📂 Global Talent Pool")
        
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                # Top Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Candidates", len(df))
                m2.metric("Avg Score", f"{int(df['score'].mean())}%")
                m3.metric("Top Candidate", df.sort_values(by="score", ascending=False).iloc[0]['name'])

                st.markdown("---")
                # Fancy Table
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                
                # Detailed Feedbacks
                st.subheader("🤖 AI Decision Insights")
                for _, row in df.iterrows():
                    color = "green" if row['score'] >= 70 else "orange" if row['score'] >= 40 else "red"
                    with st.expander(f"Analysis for {row['name']} - Score: {row['score']}%"):
                        st.markdown(f"**Status:** :{color}[{row['reason']}]")
                        st.write(f"**Key Skills Found:** {row['skills']}")
                        st.progress(row['score'] / 100)
            else:
                st.info("The database is currently empty.")
        except Exception as e:
            st.error("Database mismatch. Please use the reset button below.")

        st.markdown("---")
        if st.button("🗑️ Reset All Data"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
