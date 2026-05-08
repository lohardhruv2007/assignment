import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

st.set_page_config(page_title="AI Recruiter Pro", layout="wide")

# --- PRO TECH THEME (Slate & Emerald) ---
st.markdown("""
<style>
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    .stApp { background-color: #0e1117 !important; font-family: 'Inter', sans-serif !important; }
    
    .main .block-container {
        display: flex !important; flex-direction: column !important;
        justify-content: center !important; align-items: center !important;
        height: 100vh !important; max-width: 900px !important; margin: auto !important;
    }

    .portal-heading {
        font-size: 55px !important; font-weight: 800 !important;
        color: #10b981 !important; text-align: center; margin-bottom: 30px;
        text-transform: uppercase; letter-spacing: 2px;
    }

    label { font-size: 20px !important; color: #94a3b8 !important; font-weight: 500 !important; }
    
    div[data-baseweb="input"] { 
        background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px; 
    }

    input { color: #f8fafc !important; font-size: 20px !important; }

    .stButton > button {
        width: 100%; height: 65px; background-color: #10b981; color: #000;
        font-size: 24px; font-weight: 700; border-radius: 8px; border: none; margin-top: 20px;
    }
    
    .login-box {
        background-color: #161e2e; padding: 40px; border-radius: 16px;
        border: 1px solid #1f2937; width: 100%; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Login Credentials
VALID_USER = "admin"
VALID_PASS = "hr123"

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- LOGIN PAGE ---
if not st.session_state['auth']:
    st.markdown('<div class="portal-heading">System Access</div>', unsafe_allow_html=True)
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    u_input = st.text_input("Recruiter ID")
    p_input = st.text_input("Access Key", type="password")
    
    if st.button("AUTHENTICATE"):
        # Password check (Wahi hr123 hai bhai)
        if u_input == VALID_USER and p_input == VALID_PASS:
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Access Denied: Galat ID ya Password")
    st.markdown("</div>", unsafe_allow_html=True)

# --- LOGGED IN CONTENT ---
else:
    st.sidebar.markdown("<h2 style='color:#10b981;'>Admin Panel</h2>", unsafe_allow_html=True)
    if st.sidebar.button("Logout"):
        st.session_state['auth'] = False
        st.rerun()
    
    st.markdown(f'<div class="portal-heading">Welcome, {VALID_USER}</div>', unsafe_allow_html=True)
    # Baaki screener logic yahan aayega
