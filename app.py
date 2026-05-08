import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Database Initialization
init_db()

# Force Sidebar to expand natively
st.set_page_config(
    page_title="TalentFlow AI Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SAFE CSS (NO HIDING CRITICAL ELEMENTS) ---
st.markdown("""
<style>
    /* Bas background aur colors set kiye hain, koi element hide nahi kiya */
    .stApp { background-color: #0e1117 !important; color: #f8fafc; }
    
    .portal-heading {
        font-size: 50px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# Session States
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'messages' not in st.session_state: st.session_state['messages'] = []

# --- 1. SIDEBAR (Safe & Native) ---
with st.sidebar:
    st.markdown("<h1 style='color:#10b981;'>Admin Panel</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Navigation Choice
    choice = st.radio(
        "GO TO:",
        ["AI Batch Screener", "Talent Database", "AI Recruitment Bot"],
        index=0
    )
    
    st.write("---")
    if st.button("🚪 Logout System"):
        st.session_state['auth'] = False
        st.rerun()

# --- 2. AUTHENTICATION (admin/hr123) ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">System Authentication</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Recruiter ID", placeholder="admin")
            p = st.text_input("Security Key", type="password", placeholder="hr123")
            if st.form_submit_button("LOGIN"):
                if u == "admin" and p == "hr123":
                    st.session_state['auth'] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

# --- 3. MAIN CONTENT (Only after Login) ---
else:
    # PAGE 1: SCREENER (PDF Uploader)
    if choice == "AI Batch Screener":
        st.markdown('<div class="portal-heading">AI Batch Screener</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload Resumes (PDF Only)", type="pdf", accept_multiple_files=True)
        if files and st.button("EXECUTE ANALYSIS"):
            with st.status("AI Analyzing Resumes..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    data = analyze_resume(text)
                    save_candidate(f.name, data["score"], data["education"], data["notice_period"], ", ".join(data["skills"]), data["reason"])
            st.success(f"Processed {len(files)} candidates successfully!")

    # PAGE 2: DATABASE
    elif choice == "Talent Database":
        st.markdown('<div class="portal-heading">Candidate Rankings</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
            st.dataframe(df, use_container_width=True, height=500)
        except:
            st.info("No data yet. Upload resumes in the Screener section.")
        conn.close()

    # PAGE 3: AI CHATBOT
    elif choice == "AI Recruitment Bot":
        st.markdown('<div class="portal-heading">Hiring AI Bot</div>', unsafe_allow_html=True)
        
        # Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask about candidate scores..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                response = f"AI Analysis for: '{prompt}'. Based on technical criteria, prioritize candidates with high Python/SQL scores."
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
