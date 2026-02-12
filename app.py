import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import extract_text_from_pdf, analyze_resume, init_db, save_candidate

# Initialize Database
init_db()

# Force wide mode and hide default padding
st.set_page_config(page_title="TalentFlow AI Pro", page_icon="🌿", layout="wide")

# --- THE ABSOLUTE ERASER (Aggressive CSS Reset) ---
st.markdown("""
    <style>
    /* 1. HIDE EVERYTHING: Header, Footer, Main Menu, and Gaps */
    header, footer, [data-testid="stHeader"], #MainMenu {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 2. FORCE TOTAL BACKGROUND (No White Gaps) */
    .stApp {
        background-color: #f3f7f0 !important;
        font-family: 'Times New Roman', Times, serif !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 3. KILL TOP PADDING (Main Content upar chipak jayega) */
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

    /* 4. RECRUITER PORTAL HEADING (Centered & Clean) */
    .portal-heading {
        font-size: 70px !important;
        font-weight: 800 !important;
        color: #1b3022 !important;
        text-align: center !important;
        margin: 0 0 30px 0 !important;
        padding: 0 !important;
    }

    /* 5. INPUT BOXES FIX (Dark color hatakar background jaisa pastel green) */
    div[data-baseweb="input"], [data-testid="stTextInput"] > div {
        background-color: #eef2ef !important; /* Pastel Background */
        border: 2px solid #c8d6cc !important;
        border-radius: 12px !important;
        color: #1b3022 !important;
        height: 65px !important;
    }

    input {
        background-color: transparent !important;
        font-size: 26px !important;
        text-align: center !important;
        color: #1b3022 !important;
    }

    /* 6. GIANT ENTER BUTTON (Centered & Full Width) */
    .stButton > button {
        width: 100% !important;
        height: 80px !important;
        background-color: #4f6d5a !important;
        color: white !important;
        font-size: 32px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        margin-top: 20px !important;
    }

    /* 7. LOGIN BOX CARD (Pure White Clean Look) */
    .login-box {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 25px !important;
        border: 2px solid #c8d6cc !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        width: 550px !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* Sidebar huge text fix */
    [data
