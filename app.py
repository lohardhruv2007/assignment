import streamlit as st
import PyPDF2
import re
import sqlite3
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
import io

# --- 1. PAGE CONFIG & CREAM BACKGROUND ---
st.set_page_config(page_title="Resume Screener AI", page_icon="📄", layout="centered")

# Custom CSS for Cream Background (#FFFDD0)
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFDD0;
    }
    /* Text Colors for Contrast */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #333333 !important;
    }
    /* Button Styling */
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        border: none;
    }
    /* Success Message Box */
    .stSuccess {
        background-color: #D4EDDA;
        color: #155724;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. ROBUST DATABASE FUNCTIONS ---
def init_db():
    """Database initialize karega, aur agar schema galat hai to fix karega."""
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    # Check if table exists
    c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='candidates' ''')
    if c.fetchone()[0] == 1:
        # Table exists, check columns
        c.execute('PRAGMA table_info(candidates)')
        columns = c.fetchall()
        # Agar columns 5 nahi hain (purana version hai), to table drop kardo
        if len(columns) != 5:
            c.execute('DROP TABLE candidates')
            conn.commit()
            
    # Create fresh table
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (name TEXT, score INTEGER, education TEXT, skills TEXT, reason TEXT)''')
    conn.commit()
    conn.close()

def save_candidate(name, score, education, skills, reason):
    """Candidate data save karega with Auto-Correction."""
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    # Skills list to string
    skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
    
    try:
        # Koshish karein data dalne ki
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", 
                  (name, score, education, skills_str, reason))
        conn.commit()
    except sqlite3.OperationalError:
        # Agar "Column Mismatch" error aaye, to table recreate karo
        c.execute("DROP TABLE IF EXISTS candidates")
        init_db() # Re-create table
        # Wapas insert karo
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", 
                  (name, score, education, skills_str, reason))
        conn.commit()
    
    conn.close()

# --- 3. TEXT EXTRACTION (OCR INCLUDED) ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        
        # Pehle 3 pages read karein
        for page in pdf_reader.pages[:3]:
            content = page.extract_text()
            if content:
                text += content + " "
        
        # Agar text khali hai (Scanned PDF), to OCR use karein
        if len(text.strip()) < 50:
            with st.spinner("⚠️ Scanned Image Detected! Extracting text via OCR..."):
                uploaded_file.seek(0)
                images = convert_from_bytes(uploaded_file.read())
                for img in images[:2]: # First 2 pages only for speed
                    text += pytesseract.image_to_string(img)
                    
        return re.sub(r'\s+', ' ', text).strip()
    except Exception as e:
        st.error(f"Error parsing PDF: {e}")
        return ""

# --- 4. SCORING LOGIC ---
def analyze_resume(text):
    res = {"education": "Unknown", "skills": [], "score": 25, "reason": ""}
    
    if not text:
        res["reason"] = "Rejected: File unreadable or empty."
        return res

    # Education Check
    has_degree = False
    # Added common Indian degrees
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering|B\.E\.|M\.C\.A|B\.C\.A|Techno India', text, re.I):
        res["education"] = "Technical Degree (B.Tech/BE/MCA)"
        res["score"] += 45
        has_degree = True
    elif re.search(r'B\.Sc|M\.Sc|Bachelor\s*of\s*Science', text, re.I):
        res["education"] = "Science Degree (B.Sc/M.Sc)"
        res["score"] += 30

    # Skills Check
    skill_list = ["Python", "Java", "C\+\+", "SQL", "MySQL", "JavaScript", "HTML", "CSS", "React", "Node", "AWS", "Git", "Machine Learning", "Excel"]
    found_skills = []
    for skill in skill_list:
        # Clean regex to match exact words
        pattern = r'\b' + skill.replace("+", "\+") + r'\b'
        if re.search(pattern, text, re.I):
