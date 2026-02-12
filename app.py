import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- ULTRA MAX CENTERED CSS ---
st.markdown("""
    <style>
    /* 1. Reset and Center Everything */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
        height: 100vh !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* Main Container Center */
    .main .block-container {
        max-width: 900px !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        height: 80vh !important;
    }

    /* 2. HUGE FONTS */
    h1 { 
        font-size: 80px !important; 
        text-align: center !important;
        color: #1b3022 !important; 
        font-weight: 900 !important;
        margin-bottom: 30px !important;
    }

    p, span, label, .stMarkdown {
        font-size: 32px !important;
        text-align: center !important;
        color: #1b3022 !important;
    }

    /* 3. CENTERED INPUT BOXES (Pastel Green) */
    div[data-baseweb="input"] {
        background-color: #e0eadd !important;
        border: 3px solid #c8d6cc !important;
        border-radius: 15px !important;
        height: 70px !important;
        margin-bottom: 20px !important;
    }
    
    input {
        font-size: 30px !important;
        text-align: center !important;
        padding: 10px !important;
    }

    /* 4. MASSIVE CENTERED BUTTON */
    .stButton>button {
        width: 100% !important;
        height: 100px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 40px !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
        margin-top: 20px !important;
    }

    /* 5. CENTERED CARD */
    .card {
        background-color: white !important;
        padding: 60px !important;
        border-radius: 30px !important;
        border: 3px solid #c8d6cc !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    /* Sidebar Font Fix */
    [data-testid="stSidebar"] * {
        font-size: 26px !important;
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN PAGE ---
if not st.session_state['logged_in']:
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("💼 Recruiter Portal")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    user = st.text_input("Username", placeholder="admin")
    pwd = st.text_input("Password", type="password", placeholder="hr123")
    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Screener"
            st.rerun()
        else: st.error("Access Denied")
    st.markdown("</div>", unsafe_allow_html=True)

# --- APP FLOW ---
else:
    with st.sidebar:
        st.markdown("<h1>🌿 TalentFlow</h1>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🔍 New Screening"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Database"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"): st.session_state['logged_in'] = False; st.rerun()

    # SCREENER PAGE
    if st.session_state['page'] == "Screener":
        st.title("🔍 Resume Screening")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        files = st.file_uploader("Drop PDF files here", type="pdf", accept_multiple_files=True)
        if files and st.button("🚀 START RANKING"):
            with st.status("AI Agent Processing...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                s.update(label="Complete!", state="complete")
            st.session_state['page'] = "Database"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # DATABASE PAGE
    elif st.session_state['page'] == "Database":
        st.title("📂 Candidate Pool")
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                
                for _, row in df.iterrows():
                    with st.expander(f"Report: {row['name']}"):
                        st.write(f"**Reason:** {row['reason']}")
                        st.progress(row['score'] / 100)
            else: st.info("Database is empty.")
        except: st.error("Database mismatch. Please reset.")

        if st.button("🗑️ RESET DATABASE"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
