import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

# Page config to force wide mode
st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- THE ABSOLUTE ERASER CSS (No Bars, No Margins, Pure Centered) ---
st.markdown("""
    <style>
    /* 1. HIDE ALL STREAMLIT BARS & PADDING */
    [data-testid="stHeader"], footer, #MainMenu {display: none !important;}
    
    /* 2. FORCE FULL SCREEN BACKGROUND */
    .stApp {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* 3. CENTER EVERYTHING & KILL TOP WHITE SPACE */
    .main .block-container {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        height: 100vh !important;
        padding: 0 !important;
        margin-top: -50px !important; /* Forces content up to hide gaps */
    }

    /* 4. RECRUITER PORTAL HEADING (CLEAN & CENTERED) */
    .portal-heading {
        font-size: 75px !important;
        font-weight: 800 !important;
        color: #1b3022 !important;
        text-align: center !important;
        margin-bottom: 20px !important;
        width: 100% !important;
    }

    /* 5. PERFECT CENTER CARD (LOGIN BOX) */
    .login-box {
        background-color: white !important;
        padding: 50px !important;
        border-radius: 25px !important;
        border: 2px solid #c8d6cc !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08) !important;
        width: 550px !important; /* Fixed width for better look */
        display: flex !important;
        flex-direction: column !important;
        gap: 15px !important;
    }

    /* 6. INPUT BOXES FIX (NO DARK COLOR) */
    div[data-baseweb="input"] {
        background-color: #eef2ef !important;
        border: 2px solid #c8d6cc !important;
        border-radius: 12px !important;
        height: 65px !important;
    }

    input {
        font-size: 26px !important;
        text-align: center !important;
        color: #1b3022 !important;
    }

    /* 7. GIANT ENTER BUTTON */
    .stButton>button {
        width: 100% !important;
        height: 85px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 32px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        margin-top: 20px !important;
    }

    .stButton>button:hover {
        background-color: #3a5142 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Session States
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- LOGIN FLOW ---
if not st.session_state['logged_in']:
    # Clean Heading
    st.markdown('<div class="portal-heading">Recruiter Portal</div>', unsafe_allow_html=True)
    
    # Login Card
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    user = st.text_input("User", placeholder="admin", label_visibility="collapsed")
    pwd = st.text_input("Pass", type="password", placeholder="hr123", label_visibility="collapsed")
    
    if st.button("ENTER DASHBOARD"):
        if user == "admin" and pwd == "hr123":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PROTECTED APP CONTENT ---
else:
    st.title("🌿 Welcome to TalentFlow")
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()
