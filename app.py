import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# ---------- CLEAN FINAL CSS ----------
st.markdown("""
<style>
[data-testid="stHeader"], footer, #MainMenu {
    display: none !important;
}

.stApp {
    background-color: #f3f7f0 !important;
    font-family: 'Times New Roman', Times, serif !important;
}

.main .block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    height: 100vh !important;
    max-width: 100% !important;
}

.portal-heading {
    font-size: 70px !important;
    font-weight: 800 !important;
    color: #1b3022 !important;
    text-align: center !important;
    margin-bottom: 40px !important;
}

/* 🔥 FIXED INPUT STYLE */
[data-testid="stTextInput"] {
    width: 550px !important;
}

[data-testid="stTextInput"] > div {
    background: rgba(255,255,255,0.4) !important;
    border: 2px solid #c8d6cc !important;
    border-radius: 14px !important;
    backdrop-filter: blur(6px);
}

[data-testid="stTextInput"] input {
    background: transparent !important;
    color: #1b3022 !important;
    font-size: 26px !important;
    text-align: center !important;
    padding: 18px !important;
}

[data-testid="stTextInput"] > div:focus-within {
    border: 2px solid #4f6d5a !important;
    box-shadow: none !important;
}

.stButton > button {
    width: 550px !important;
    height: 80px !important;
    background-color: #4f6d5a !important;
    color: white !important;
    font-size: 28px !important;
    font-weight: bold !important;
    border-radius: 15px !important;
    border: none !important;
    margin-top: 25px !important;
}

[data-testid="stSidebar"] * {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = "Login"

# ---------- LOGIN ----------
if not st.session_state['logged_in']:

    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)

    user = st.text_input("", placeholder="admin")
    pwd = st.text_input("", type="password", placeholder="hr123")

    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.session_state['page'] = "Screener"
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------- APP ----------
else:

    with st.sidebar:
        st.markdown("<h2 style='color:#4f6d5a;'>🌿 TalentFlow AI</h2>", unsafe_allow_html=True)

        if st.button("🔍 New Screening"):
            st.session_state['page'] = "Screener"
            st.rerun()

        if st.button("📊 Talent Database"):
            st.session_state['page'] = "Database"
            st.rerun()

        if st.button("🚪 Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    if st.session_state['page'] == "Screener":

        st.markdown('<div class="portal-heading" style="font-size:50px;">Resume Screening</div>', unsafe_allow_html=True)

        files = st.file_uploader("Upload Resumes", type="pdf", accept_multiple_files=True)

        if files and st.button("START ANALYSIS"):
            with st.status("Analyzing..."):
                for f in files:
                    text = extract_text_from_pdf(f)
                    res = analyze_resume(text)
                    save_candidate(
                        f.name,
                        res["score"],
                        res["education"],
                        res["notice_period"],
                        ", ".join(res["skills"]),
                        res["reason"]
                    )
            st.session_state['page'] = "Database"
            st.rerun()

    elif st.session_state['page'] == "Database":

        st.markdown('<div class="portal-heading" style="font-size:50px;">Candidate Pool</div>', unsafe_allow_html=True)

        conn = sqlite3.connect('candidates.db')
        df = pd.read_sql_query("SELECT * FROM candidates", conn)

        if not df.empty:
            st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)

        if st.button("RESET DATABASE"):
            if os.path.exists('candidates.db'):
                os.remove('candidates.db')
            st.rerun()

        conn.close()
