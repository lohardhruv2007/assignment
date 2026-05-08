import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

# Page Config: Sidebar hamesha expanded rahega
st.set_page_config(
    page_title="TalentFlow AI Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CLEAN DARK THEME (Zero Sidebar Clash) ---
st.markdown("""
<style>
    /* Hide Only Header and Footer */
    [data-testid="stHeader"], footer {display: none !important;}
    
    .stApp { background-color: #0e1117 !important; color: #f8fafc; }
    
    .portal-heading {
        font-size: 50px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 25px;
    }

    /* Professional Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161e2e !important;
        border-right: 1px solid #1f2937;
    }
</style>
""", unsafe_allow_html=True)

# Session States
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'page' not in st.session_state: st.session_state['page'] = "AI Batch Screener"
if 'messages' not in st.session_state: st.session_state['messages'] = []

# --- 1. SIDEBAR NAVIGATION (Hamesha Visible) ---
with st.sidebar:
    st.markdown("<h1 style='color:#10b981;'>Admin Panel</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Navigation Radio (Isse sidebar kabhi gayab nahi hoga)
    choice = st.radio(
        "GO TO:",
        ["AI Batch Screener", "Talent Database", "AI Recruitment Bot"],
        index=0
    )
    
    st.write("---")
    if st.button("🚪 Logout System"):
        st.session_state['auth'] = False
        st.rerun()

# --- 2. AUTHENTICATION LOGIC ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">System Authentication</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("auth_form"):
            u = st.text_input("Recruiter ID", placeholder="admin")
            p = st.text_input("Security Key", type="password", placeholder="hr123")
            if st.form_submit_button("LOGIN"):
                if u == "admin" and p == "hr123":
                    st.session_state['auth'] = True
                    st.rerun()
                else:
                    st.error("Invalid Access Key")
    st.info("Sidebar is disabled until login.")

# --- 3. MAIN DASHBOARD CONTENT (Login ke baad) ---
else:
    # Page 1: Screener (PDF Uploader)
    if choice == "AI Batch Screener":
        st.markdown('<div class="portal-heading">Batch AI Resume Screener</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload Batch Resumes (PDF Only)", type="pdf", accept_multiple_files=True)
        if files and st.button("RUN SYSTEM ANALYSIS"):
            with st.status("AI Agent Analyzing PDFs..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
            st.success(f"Successfully processed {len(files)} resumes.")

    # Page 2: Database
    elif choice == "Talent Database":
        st.markdown('<div class="portal-heading">Candidate Analytics</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
            st.dataframe(df, use_container_width=True, height=500)
        except:
            st.warning("No data found. Upload resumes in the Screener section.")
        conn.close()

    # Page 3: AI Chatbot
    elif choice == "AI Recruitment Bot":
        st.markdown('<div class="portal-heading">Recruitment AI Bot</div>', unsafe_allow_html=True)
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about B.Tech hiring criteria..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                response = f"Analyzing candidates for: '{prompt}'. Based on the data, B.Tech graduates with Python/SQL are currently ranked highest."
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
