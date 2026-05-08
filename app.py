import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Fresh start
init_db()

st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- THE ABSOLUTE CLEAN UI (ERASER MODE) ---
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    
    /* Background & Classic Font */
    .stApp {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* Vertical & Horizontal Center */
    .main .block-container {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        height: 100vh !important;
        max-width: 800px !important;
        margin: auto !important;
    }

    .portal-heading {
        font-size: 65px !important;
        font-weight: 800 !important;
        color: #1b3022 !important;
        text-align: center !important;
        margin-bottom: 30px !important;
    }

    label { font-size: 26px !important; font-weight: bold; color: #1b3022; }
    
    /* Input Boxes (No Navy Blue) */
    div[data-baseweb="input"] {
        background-color: #eef2ef !important;
        border: 2px solid #c8d6cc !important;
        border-radius: 12px !important;
    }

    input { font-size: 28px !important; text-align: center !important; }

    .stButton > button {
        width: 100% !important; height: 85px !important;
        background-color: #4f6d5a !important; color: white !important;
        font-size: 32px !important; font-weight: bold !important;
        border-radius: 15px !important; margin-top: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)
    with st.container():
        # Labels are back!
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("ENTER DASHBOARD"):
            if user == "admin" and pwd == "hr123":
                st.session_state['auth'] = True
                st.rerun()
            else: st.error("Access Denied")
else:
    # Dashboard code here
    st.sidebar.title("🌿 TalentFlow")
    if st.sidebar.button("Logout"):
        st.session_state['auth'] = False
        st.rerun()
    st.markdown('<div class="portal-heading">Welcome to Dashboard</div>', unsafe_allow_html=True)
