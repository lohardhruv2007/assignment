import streamlit as st
import pandas as pd
import sqlite3
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

init_db()
st.set_page_config(page_title="Recruiter Admin", layout="wide")

# --- PRO TECH THEME (Emerald & Slate) ---
st.markdown("""
<style>
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    .stApp { background-color: #0e1117 !important; font-family: 'Inter', sans-serif !important; }
    
    .main .block-container {
        display: flex !important; flex-direction: column !important;
        justify-content: center !important; align-items: center !important;
        height: 100vh !important; max-width: 900px !important; margin: auto !important;
    }

    .portal-heading {
        font-size: 55px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 30px;
        text-transform: uppercase; letter-spacing: 2px;
    }

    label { font-size: 20px !important; color: #94a3b8 !important; font-weight: 500 !important; }
    
    div[data-baseweb="input"] { 
        background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px; 
    }

    input { color: #f8fafc !important; font-size: 20px !important; }

    .stButton > button {
        width: 100%; height: 65px; background-color: #10b981; color: #000;
        font-size: 24px; font-weight: 700; border-radius: 8px; border: none; margin-top: 20px;
    }
    
    .login-box {
        background-color: #161e2e; padding: 40px; border-radius: 16px;
        border: 1px solid #1f2937; width: 100%; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">System Access</div>', unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    u = st.text_input("Recruiter ID")
    p = st.text_input("Access Key", type="password")
    if st.button("AUTHENTICATE"):
        if u == "admin" and p == "hr123":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Access Denied")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<h2 style='color:#10b981;'>Admin Panel</h2>", unsafe_allow_html=True)
    page = st.sidebar.radio("Navigate", ["Resume Screener", "Analytics"])
    if page == "Resume Screener":
        st.markdown('<div class="portal-heading">Screener</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload Batch Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("RUN ANALYSIS"):
            for f in files:
                t = extract_text_from_pdf(f)
                r = analyze_resume(t)
                save_candidate(f.name, r["score"], r["education"], r["notice_period"], ", ".join(r["skills"]), r["reason"])
            st.success("Batch Analysis Complete.")
    else:
        st.markdown('<div class="portal-heading">Talent Data</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        st.dataframe(df, use_container_width=True)
        if st.sidebar.button("Logout"):
            st.session_state['auth'] = False
            st.rerun()
        conn.close()
