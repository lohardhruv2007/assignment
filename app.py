import streamlit as st
import pandas as pd
import sqlite3
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

init_db()
st.set_page_config(page_title="AI Recruiter Pro", layout="wide")

# --- TECH-LEVEL CSS (Slate & Emerald) ---
st.markdown("""
<style>
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    .stApp { background-color: #0e1117 !important; font-family: 'Inter', sans-serif !important; }
    
    .main .block-container {
        padding-top: 2rem !important;
        max-width: 1000px !important;
        margin: auto !important;
    }

    .portal-heading {
        font-size: 50px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 40px;
        letter-spacing: -1px;
    }

    .login-box {
        background-color: #161e2e; padding: 50px; border-radius: 20px;
        border: 1px solid #1f2937; width: 100%; box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    }

    label { font-size: 18px !important; color: #94a3b8 !important; }
    div[data-baseweb="input"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px; }
    input { color: #f8fafc !important; font-size: 18px !important; }

    .stButton > button {
        width: 100%; height: 60px; background-color: #10b981; color: #000;
        font-size: 22px; font-weight: 700; border-radius: 10px; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">AI Recruiter Access</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        u = st.text_input("Recruiter ID")
        p = st.text_input("Security Key", type="password")
        if st.button("LOGIN TO SYSTEM"):
            if u == "admin" and p == "hr123":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Authentication Failed")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<h2 style='color:#10b981;'>AI Command Center</h2>", unsafe_allow_html=True)
    page = st.sidebar.radio("Navigate", ["AI Screener", "Talent Database"])
    
    if page == "AI Screener":
        st.markdown('<div class="portal-heading">AI Resume Analysis</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload Batch PDF Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("EXECUTE AI SCAN"):
            with st.status("AI Agent scanning resumes...", expanded=True):
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
            st.success("Analysis Complete. Check Database.")
    
    else:
        st.markdown('<div class="portal-heading">Candidate Rankings</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
        st.dataframe(df, use_container_width=True)
        if st.sidebar.button("Logout"):
            st.session_state['auth'] = False
            st.rerun()
        conn.close()
