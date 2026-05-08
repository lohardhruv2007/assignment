import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initializing DB
init_db()

# Page Config: Force sidebar state to expanded
st.set_page_config(
    page_title="TalentFlow AI Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MINIMALIST CSS (Will NOT hide Sidebar) ---
st.markdown("""
<style>
    /* Hide Only Header/Footer */
    [data-testid="stHeader"], footer {display: none !important;}
    
    .stApp { background-color: #0e1117 !important; color: white; }
    
    .portal-heading {
        font-size: 45px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Login logic using session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- AUTHENTICATION ---
if not st.session_state['authenticated']:
    st.markdown('<div class="portal-heading">System Access</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        u = st.text_input("User ID")
        p = st.text_input("Access Key", type="password")
        if st.form_submit_button("AUTHENTICATE"):
            if u == "admin" and p == "hr123":
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

# --- MAIN DASHBOARD (Visible Only After Auth) ---
else:
    # YE SIDEBAR AB NAHI GAYAB HOGA
    st.sidebar.title("🌿 TalentFlow AI")
    st.sidebar.write("---")
    
    # Navigation using Sidebar Radio (Bulletproof)
    choice = st.sidebar.radio(
        "NAVIGATION MENU",
        ["AI Batch Screener", "Talent Database", "AI Hiring Bot"]
    )
    
    st.sidebar.write("---")
    if st.sidebar.button("Logout"):
        st.session_state['authenticated'] = False
        st.rerun()

    # 1. SCREENER PAGE
    if choice == "AI Batch Screener":
        st.markdown('<div class="portal-heading">Batch AI Analysis</div>', unsafe_allow_html=True)
        files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
        if files and st.button("RUN SCAN"):
            for f in files:
                text = extract_text_from_pdf(f)
                res = analyze_resume(text)
                save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
            st.success("Analysis Finished.")

    # 2. DATABASE PAGE
    elif choice == "Talent Database":
        st.markdown('<div class="portal-heading">Talent Database</div>', unsafe_allow_html=True)
        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY score DESC", conn)
        st.dataframe(df, use_container_width=True)
        conn.close()

    # 3. CHATBOT PAGE
    elif choice == "AI Hiring Bot":
        st.markdown('<div class="portal-heading">HR AI Assistant</div>', unsafe_allow_html=True)
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about B.Tech candidates..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                response = f"Analyzing candidates for your query: '{prompt}'."
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
