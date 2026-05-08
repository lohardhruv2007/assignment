import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Step 1: Initialize Database
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- PRO TECH THEME (Emerald & Slate) ---
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    
    /* Background & Global Font */
    .stApp { 
        background-color: #0e1117 !important; 
        font-family: 'Inter', sans-serif !important; 
    }
    
    /* Centering and Margins */
    .main .block-container {
        padding-top: 2rem !important;
        max-width: 1100px !important;
        margin: auto !important;
    }

    .portal-heading {
        font-size: 50px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 30px;
    }

    /* Professional Card Look */
    .glass-card {
        background-color: #161e2e; padding: 40px; border-radius: 20px;
        border: 1px solid #1f2937; width: 100%; box-shadow: 0 25px 50px rgba(0,0,0,0.5);
    }

    label { font-size: 20px !important; color: #94a3b8 !important; }
    div[data-baseweb="input"] { background-color: #1e293b !important; border-radius: 8px; border: 1px solid #334155 !important; }
    input { color: #f8fafc !important; font-size: 18px !important; }

    .stButton > button {
        width: 100%; height: 60px; background-color: #10b981; color: #000;
        font-size: 22px; font-weight: 700; border-radius: 10px; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Session States for Authentication and Navigation
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Screener"
if 'messages' not in st.session_state: st.session_state['messages'] = []

# --- 1. LOGIN SYSTEM (admin/hr123) ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">AI Recruiter Access</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        u = st.text_input("Recruiter ID")
        p = st.text_input("Security Key", type="password")
        if st.button("AUTHENTICATE SYSTEM"):
            if u == "admin" and p == "hr123":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Access Denied: Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. MAIN DASHBOARD (With Sidebar) ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#10b981;'>Admin Panel</h2>", unsafe_allow_html=True)
        st.markdown("---")
        if st.sidebar.button("🔍 AI Resume Screener"):
            st.session_state['page'] = "Screener"
            st.rerun()
        if st.sidebar.button("📊 Talent Database"):
            st.session_state['page'] = "Database"
            st.rerun()
        if st.sidebar.button("🤖 AI Recruitment Bot"):
            st.session_state['page'] = "Chatbot"
            st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Logout"):
            st.session_state['auth'] = False
            st.rerun()

    # --- PAGE 1: AI SCREENER (PDF Uploader) ---
    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading">Batch AI Screener</div>', unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        files = st.file_uploader("Upload Resumes (PDF Only)", type="pdf", accept_multiple_files=True)
        if files and st.button("EXECUTE BATCH SCAN"):
            with st.status("AI Agent analyzing resumes...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
                s.update(label="Scanning Complete!", state="complete")
            st.success(f"Processed {len(files)} resumes successfully.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PAGE 2: DATABASE ---
    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading">Candidate Rankings</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
            if not df.empty:
                st.dataframe(df, use_container_width=True, height=500)
            else:
                st.info("Database is empty. Please run the screener first.")
        except:
            st.error("Database mismatch. Use 'Reset' if errors persist.")
        
        if st.button("RESET DATABASE"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()

    # --- PAGE 3: AI CHATBOT ---
    elif st.session_state['page'] == "Chatbot":
        st.markdown('<div class="portal-heading">HR Intelligence Bot</div>', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about candidates or hiring criteria..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                response = f"Analyzing recruitment data for: '{prompt}'. Currently, we are prioritizing B.Tech candidates with Python and SQL skills."
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
