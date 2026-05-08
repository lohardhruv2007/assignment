import streamlit as st
import pandas as pd
import sqlite3
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

init_db()
st.set_page_config(page_title="TalentFlow AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- TECH THEME CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117 !important; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .portal-heading {
        font-size: 45px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 20px;
    }
    .stSidebar { background-color: #161e2e !important; border-right: 1px solid #1f2937; }
    div[data-baseweb="input"] { background-color: #1e293b !important; border-radius: 8px; }
    .stButton > button { width: 100%; background-color: #10b981; color: #000; font-weight: 700; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Session States
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'page' not in st.session_state: st.session_state['page'] = "AI Screener"
if 'chat_history' not in st.session_state: st.session_state['chat_history'] = []

# --- LOGIN (admin / hr123) ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">System Access</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("User ID")
        p = st.text_input("Access Key", type="password")
        if st.button("LOGIN"):
            if u == "admin" and p == "hr123":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Access Denied")

# --- LOGGED IN CONTENT ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#10b981;'>Admin Menu</h2>", unsafe_allow_html=True)
        if st.button("🔍 AI Resume Screener"): st.session_state['page'] = "Screener"
        if st.button("📊 Talent Pool"): st.session_state['page'] = "Database"
        if st.button("🤖 AI HR Chatbot"): st.session_state['page'] = "Chatbot"
        st.write("---")
        if st.button("Logout"): 
            st.session_state['auth'] = False
            st.rerun()

    if st.session_state['page'] == "Screener":
        st.markdown('<div class="portal-heading">Batch AI Screener</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("RUN AI SCAN"):
            for f in files:
                t = extract_text_from_pdf(f)
                r = analyze_resume(t)
                save_candidate(f.name, r["score"], r["education"], "30 Days", ", ".join(r["skills"]), r["reason"])
            st.success("Batch Analysis Complete!")

    elif st.session_state['page'] == "Database":
        st.markdown('<div class="portal-heading">Candidate Rankings</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
        st.dataframe(df, use_container_width=True)
        conn.close()

    # --- AI CHATBOT SECTION ---
    elif st.session_state['page'] == "Chatbot":
        st.markdown('<div class="portal-heading">AI Hiring Assistant</div>', unsafe_allow_html=True)
        
        # Display Chat History
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask me about hiring or candidates..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                response = f"Scanning Talent Pool for: '{prompt}'. I suggest prioritizing B.Tech graduates with Python/SQL skills for this role."
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
