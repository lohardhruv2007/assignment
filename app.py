import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- FULL PASTEL GREEN OVERRIDE ---
st.markdown("""
    <style>
    /* 1. Main Background Override */
    .stApp {
        background: linear-gradient(135deg, #f3f7f0 0%, #e0eadd 100%) !important;
    }

    /* 2. Sidebar Background & Text Fix */
    [data-testid="stSidebar"] {
        background-color: #eef2ef !important;
        border-right: 2px solid #c8d6cc !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #2d3e33 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* 3. Global Font & Color */
    * {
        font-family: 'Times New Roman', Times, serif !important;
    }
    
    h1, h2, h3, p, span, label {
        color: #1b3022 !important;
    }

    /* 4. Professional Cards */
    .stmarkdown, .card, [data-testid="stExpander"], .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 1px solid #c8d6cc !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }

    /* 5. Elegant Moss Green Buttons */
    .stButton>button {
        background-color: #4f6d5a !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: 0.3s !important;
    }

    .stButton>button:hover {
        background-color: #3a5142 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }

    /* 6. File Uploader Fix */
    [data-testid="stFileUploader"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'page' not in st.session_state: st.session_state['page'] = "Login"

# --- LOGIN ---
if not st.session_state['logged_in']:
    _, col2, _ = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("💼 Recruiter Portal")
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Enter Dashboard"):
            if user == "admin" and pwd == "hr123":
                st.session_state['logged_in'] = True
                st.session_state['page'] = "Screener"
                st.rerun()
            else: st.error("Access Denied: Use admin/hr123")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PROTECTED APP ---
else:
    with st.sidebar:
        st.title("🌿 TalentFlow")
        st.markdown("---")
        if st.button("🔍 New Screening"): st.session_state['page'] = "Screener"; st.rerun()
        if st.button("📊 Talent Database"): st.session_state['page'] = "Database"; st.rerun()
        st.markdown("---")
        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    if st.session_state['page'] == "Screener":
        st.header("🔍 Intelligent Resume Screening")
        st.write("Current Theme: English Pastel Green")
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        files = st.file_uploader("Drop PDF files here (Max 1GB)", type="pdf", accept_multiple_files=True)
        if files and st.button("🚀 Start Analysis"):
            with st.status("AI Agent Processing...", expanded=True) as s:
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(f.name, res["score"], res["education"], res["notice_period"], ", ".join(res["skills"]), res["reason"])
                s.update(label="Scanning Complete!", state="complete")
            st.session_state['page'] = "Database"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state['page'] == "Database":
        st.header("📂 Analyzed Talent Pool")
        conn = sqlite3.connect('candidates.db')
        try:
            df = pd.read_sql_query("SELECT * FROM candidates", conn)
            if not df.empty:
                m1, m2 = st.columns(2)
                m1.metric("Total Profiles", len(df))
                m2.metric("Highest Score", f"{int(df['score'].max())}%")
                
                st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
                
                st.subheader("Decision Breakdown")
                for _, row in df.iterrows():
                    color = "green" if row['score'] >= 70 else "orange" if row['score'] >= 40 else "red"
                    with st.expander(f"Analysis for {row['name']}"):
                        st.markdown(f"**AI Status:** :{color}[{row['reason']}]")
                        st.write(f"**Identified Skills:** {row['skills']}")
                        st.progress(row['score'] / 100)
            else: st.info("Database is empty.")
        except: st.error("Schema mismatch. Please Reset.")

        if st.button("🗑️ Clear History"):
            conn.close()
            if os.path.exists('candidates.db'): os.remove('candidates.db')
            st.rerun()
        conn.close()
