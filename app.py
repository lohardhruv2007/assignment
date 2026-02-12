import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

init_db()
st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- FULL PASTEL GREEN & TIMES NEW ROMAN CSS ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f3f7f0 0%, #e0eadd 100%);
        font-family: 'Times New Roman', Times, serif;
    }
    .stmarkdown, .card, [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(79, 109, 90, 0.1);
        border: 1px solid #c8d6cc;
        margin-bottom: 20px;
    }
    h1, h2, h3, p, span, div, label {
        font-family: 'Times New Roman', Times, serif !important;
        color: #2d3e33 !important;
    }
    h1 { font-weight: bold; color: #1b3022 !important; border-bottom: 2px solid #4f6d5a; }
    
    section[data-testid="stSidebar"] {
        background-color: #eef2ef !important;
        border-right: 2px solid #d1dbd3;
    }
    .stButton>button {
        background-color: #4f6d5a !important;
        color: #ffffff !important;
        border-radius: 12px;
        font-family: 'Times New Roman', Times, serif;
        font-weight: bold;
        border: 1px solid #3a5142;
        padding: 0.6rem 1rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #769482 !important;
        transform: translateY(-1px);
    }
    [data-testid="stMetricValue"] { color: #2d6a4f !important; font-weight: bold; }
    .stProgress > div > div > div > div { background-color: #4f6d5a !important; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

if not st.session_state['logged_in']:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("💼 Recruiter Portal")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Enter Dashboard"):
            if user == "admin" and pwd == "hr123":
                st.session_state['logged_in'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else: st.error("Use admin/hr123")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    with st.sidebar:
        st.header("🌿 TalentFlow AI")
        if st.button("🔍 New Screening"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Insights"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout"): st.session_state['logged_in'] = False; st.rerun()

    if st.session_state['page'] == "Screener":
        st.header("🔍 Intelligent Resume Screening")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        files = st.file_uploader("Drop PDF resumes (Max 1GB)", type="pdf", accept_multiple_files=True)
        if files and st.button("🚀 Analyze Candidates"):
            with st.status("AI Agent Processing...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                s.update(label="Scanning Complete!", state="complete")
            st.session_state['page'] = "Database"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state['page'] == "Database":
        st.header("📂 Talent Analytics Pool")
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                m1, m2, m3 = st.columns(3)
                m1.metric("Processed", len(df))
                m2.metric("Avg Score", f"{int(df['score'].mean())}%")
                m3.metric("Top Talent", df.sort_values(by="score", ascending=False).iloc[0]['name'])
                st.markdown("---")
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                st.subheader("🤖 AI Rationalization")
                for _, row in df.iterrows():
                    color = "green" if row['score'] >= 70 else "orange" if row['score'] >= 40 else "red"
                    with st.expander(f"Report: {row['name']}"):
                        st.markdown(f"**Decision:** :{color}[{row['reason']}]")
                        st.write(f"**Skills:** {row['skills']}")
                        st.progress(row['score'] / 100)
            else: st.info("No data available.")
        except: st.error("Database error. Please reset.")

        if st.button("🗑️ Clear History"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
