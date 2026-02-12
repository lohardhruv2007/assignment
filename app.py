import streamlit as st
import PyPDF2
import re
import sqlite3
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import io

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Resume Screener AI", page_icon="📄", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* MAIN PAGE */
    .stApp { background-color: #FFFDD0; }
    
    /* TEXT COLORS */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, li, div { color: #000000 !important; }
    
    /* INPUT FIELDS */
    .stTextInput > div > div > input { color: #000000 !important; background-color: #FFFFFF !important; border: 1px solid #ccc; }

    /* DRAG & DROP AREA */
    [data-testid="stFileUploader"] { background-color: #262730; border-radius: 10px; padding: 10px; }
    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] div { color: #FFFFFF !important; }
    
    /* BUTTONS */
    .stButton>button { background-color: #FF4B4B; color: white !important; border-radius: 8px; border: none; font-weight: bold; }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #E6D9B8; border-right: 1px solid #C4B490; }
    [data-testid="stSidebar"] * { color: #2C2C2C !important; }

    /* CARDS */
    .info-box { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .resume-box { background-color: #FFFFFF; border: 1px solid #CCCCCC; padding: 15px; border-radius: 5px; font-family: 'Courier New', Courier, monospace; font-size: 14px; color: #333333 !important; height: 250px; overflow-y: scroll; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); white-space: pre-wrap; }
    .candidate-card { background-color: #FFFFFF; padding: 15px; border-radius: 10px
