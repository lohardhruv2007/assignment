import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

init_db()
st.set_page_config(page_title="TalentFlow AI", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    .stApp { background-color: #f3f7f0 !important; font-family: 'Times New Roman', Times, serif !important; }
    .main .block-container {
        display: flex !important; flex-direction: column !important;
        justify-content: center !important; align-items: center !important;
        height: 100vh !important; max-width: 800px !important; margin: auto !important;
    }
    .portal-heading { font-size: 60px !important; font-weight: bold; color: #1b3022; text-align: center; margin-bottom: 20px; }
    label { font-size: 24px !important; font-weight: bold; color: #1b3022; }
    div[data-baseweb="input"] { background-color: #eef2ef !important; border: 2px solid #c8d6cc !important; border-radius: 10px; }
    input { font-size: 22px !important; text-align: center; color: #1b3022; }
    .stButton > button {
        width: 100%; height: 70px; background-color: #4f6d5a; color: white;
        font-size: 28px; font-weight: bold; border-radius: 15px; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Wrong Credentials")
else:
    st.sidebar.title("🌿 TalentFlow")
    page = st.sidebar.radio("Navigate", ["Screener", "Database"])
    if page == "Screener":
        st.markdown('<div class="portal-heading">Resume Screening</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if files and st.button("PROCESS"):
            for f in files:
                t = extract_text_from_pdf(f)
                r = analyze_resume(t)
                save_candidate(f.name, r["score"], r["education"], r["notice_period"], ", ".join(r["skills"]), r["reason"])
            st.success("Done!")
    else:
        st.markdown('<div class="portal-heading">Candidate Pool</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        st.dataframe(df, use_container_width=True)
        if st.button("LOGOUT"):
            st.session_state['auth'] = False
            st.rerun()
        conn.close()
