import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Step 1: Start Fresh
init_db()

st.set_page_config(page_title="AI Recruiter Pro", layout="wide")

# --- PROFESSIONAL DARK THEME (No Bars/Gaps) ---
st.markdown("""
<style>
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    .stApp { background-color: #0e1117 !important; font-family: 'Inter', sans-serif !important; }
    
    .main .block-container {
        padding-top: 2rem !important;
        max-width: 1100px !important;
        margin: auto !important;
    }

    .portal-heading {
        font-size: 50px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 30px;
    }

    .login-box {
        background-color: #161e2e; padding: 40px; border-radius: 20px;
        border: 1px solid #1f2937; width: 100%; box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    }

    label { font-size: 18px !important; color: #94a3b8 !important; }
    div[data-baseweb="input"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px; }
    input { color: #f8fafc !important; font-size: 18px !important; }

    .stButton > button {
        width: 100%; height: 60px; background-color: #10b981; color: #000;
        font-size: 22px; font-weight: 700; border-radius: 10px; margin-top: 20px;
    }
    
    /* Table Styling for Database */
    .stDataFrame { background-color: #161e2e !important; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Auth State
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"

# --- LOGIN PAGE ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">AI Recruiter Access</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        u = st.text_input("Recruiter ID")
        p = st.text_input("Security Key (hr123)", type="password")
        if st.button("LOGIN TO SYSTEM"):
            if u == "admin" and p == "hr123":
                st.session_state['auth'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else:
                st.error("Authentication Failed")
        st.markdown("</div>", unsafe_allow_html=True)

# --- DASHBOARD (PDF UPLOADER & DATABASE) ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#10b981;'>AI Command</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔍 AI Screener"): 
            st.session_state['page'] = "Screener"
            st.rerun()
        if st.button("📊 Database"): 
            st.session_state['page'] = "Database"
            st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            st.session_state['auth'] = False
            st.rerun()

    # 1. SCREENER PAGE (Where PDF Upload lives)
    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading">AI Batch Screener</div>', unsafe_allow_html=True)
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        
        # Ye raha tera PDF Upload wala part bhai
        files = st.file_uploader("Drop Resumes Here (PDF Only)", type="pdf", accept_multiple_files=True)
        
        if files and st.button("RUN AI ANALYSIS"):
            with st.status("AI Agent scanning resumes...", expanded=True) as status:
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
                status.update(label="Scanning Complete!", state="complete")
            st.success(f"Processed {len(files)} resumes successfully.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. DATABASE PAGE
    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading">Shortlisted Candidates</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
            if not df.empty:
                st.dataframe(df, use_container_width=True, height=400)
            else:
                st.info("No candidates analyzed yet. Go to Screener.")
        except:
            st.error("Database Error. Try resetting.")
        
        if st.button("CLEAR ALL DATA"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
