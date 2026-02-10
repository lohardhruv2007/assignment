import PyPDF2
import re
import sqlite3
import pandas as pd
import io
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

def init_db():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    # 6 Columns format: name, score, education, notice, skills, reason
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (name TEXT, score INTEGER, education TEXT, notice TEXT, skills TEXT, reason TEXT)''')
    conn.commit()
    conn.close()

def save_candidate(name, score, education, notice, skills, reason):
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    # Check if table has all columns to prevent OperationalError
    try:
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?)", (name, score, education, notice, skills, reason))
        conn.commit()
    except sqlite3.OperationalError:
        # Agar purana table milta hai toh use delete karke naya banao
        c.execute("DROP TABLE IF EXISTS candidates")
        init_db()
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?)", (name, score, education, notice, skills, reason))
        conn.commit()
    conn.close()

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        # 1GB optimized
        for page in pdf_reader.pages[:3]:
            content = page.extract_text()
            if content: text += content + " "
        
        if len(text.strip()) < 50: # OCR logic for Lucky's resume
            file.seek(0)
            images = convert_from_bytes(file.read(), first_page=1, last_page=2)
            for img in images:
                text += pytesseract.image_to_string(img)
        
        return re.sub(r'\s+', ' ', text).strip()
    except Exception:
        return ""

def analyze_resume(text):
    res = {"education": "Other", "notice_period": "90 Days (Standard)", "skills": [], "score": 25, "reason": ""}
    if not text:
        res["reason"] = "Rejected: Scanned content unreadable."
        return res

    # Education (Indian Context)
    has_degree = False
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering', text, re.I):
        res["education"] = "Technical Degree (India)"
        res["score"] += 45
        has_degree = True

    # Skills (Lucky's Stack)
    skills_map = ["Python", "Java", "PHP", "MySQL", "JavaScript", "HTML", "CSS", "Node", "Git"]
    for skill in skills_map:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.I):
            res["skills"].append(skill)
            res["score"] += 5
            
    res["score"] = min(res["score"], 100)

    # Decisions
    if res["score"] >= 70:
        res["reason"] = f"Selected: Strong degree and skills match."
    elif res["score"] >= 40:
        res["reason"] = "Waitlist: Relevant background but needs more skills."
    else:
        res["reason"] = "Rejected: Low match in degree or skills."
    
    return res
