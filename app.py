import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- CUSTOM CSS: Pastel Green & Times New Roman ---
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #f0f4f1 0%, #d9e4dd 100%);
        font-family: 'Times New Roman', Times, serif;
    }
    
    /* Card Style */
    .stmarkdown, .card, [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(46, 125, 50, 0.1);
        border: 1px solid #c8d6cc;
    }

    /* Typography */
    h1, h2, h3, p, span, div, label {
        font-family: 'Times New Roman', Times, serif !important;
        color: #2d3e33 !important;
    }

    /* Modern Button */
    .stButton>button {
        background-color: #4f6d5a;
        color: white !important;
        border-radius: 10px;
        font-family: 'Times New Roman', Times, serif;
        font-weight: bold;
        transition: 0.3s;
        border: none;
    }
    .stButton>button:hover { background-color: #3a5142; color: #fff !important; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #eef2ef;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN ---
if not st.session_state['logged_in']:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.title("💼 Recruiter Access")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "admin" and pwd == "hr123":
                st.session_state['logged_in'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else: st.error("Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)

# --- APP CONTENT ---
else:
    with st.sidebar:
        st.header("🌿 TalentFlow AI")
        if st.button("🔍 New Screening"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Database"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("---")
        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    if st.session_state['page'] == "Screener":
        st.header("🔍 Intelligent Screening")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("Start AI Analysis"):
            with st.status("Agent analyzing documents...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                s.update(label="Complete!", state="complete")
            st.session_state['page'] = "Database"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state['page'] == "Database":
        st.header("📂 Analyzed Candidates")
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                # Metrics
                c1, c2 = st.columns(2)
                c1.metric("Total Resumes", len(df))
                c2.metric("Top Score", f"{int(df['score'].max())}%")
                
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                
                st.subheader("🤖 AI Rationalization")
                for _, row in df.iterrows():
                    with st.expander(f"Report: {row['name']}"):
                        st.write(f"**Decision:** {row['reason']}")
                        st.progress(row['score'] / 100)
            else: st.info("No data yet.")
        except: st.error("Database error. Please Reset.")

        if st.button("🗑️ Reset Database"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
