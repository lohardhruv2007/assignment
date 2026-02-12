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
    # Table with Reason column
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (name TEXT, score INTEGER, education TEXT, notice TEXT, skills TEXT, reason TEXT)''')
    conn.commit()
    conn.close()

def save_candidate(name, score, education, notice, skills, reason):
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?)", (name, score, education, notice, skills, reason))
        conn.commit()
    except sqlite3.OperationalError:
        # Auto-fix if schema is old
        c.execute("DROP TABLE IF EXISTS candidates")
        init_db()
        c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?)", (name, score, education, notice, skills, reason))
        conn.commit()
    conn.close()

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        # Read only first 3 pages for speed and memory
        for page in pdf_reader.pages[:3]:
            content = page.extract_text()
            if content: text += content + " "
        
        # OCR Mode for Scanned PDFs (Lucky's Case)
        if len(text.strip()) < 50:
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
        res["reason"] = "Rejected: Document unreadable (Scanned Image/Empty)."
        return res

    # 1. Education Logic
    has_degree = False
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering|Techno India', text, re.I):
        res["education"] = "Technical Degree (India)"
        res["score"] += 45
        has_degree = True

    # 2. Skill Logic (Customized for your test cases)
    skill_list = ["Python", "Java", "PHP", "MySQL", "JavaScript", "HTML", "CSS", "Node", "Git"]
    for skill in skill_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.I):
            res["skills"].append(skill)
            res["score"] += 5
            
    res["score"] = min(res["score"], 100)

    # 3. Decision Reasoning
    if res["score"] >= 70:
        res["reason"] = f"Selected: Strong {res['education']} with skills in {', '.join(res['skills'][:2])}."
    elif res["score"] >= 40:
        res["reason"] = "Waitlist: Technical background found but lacks core skill density."
    else:
        reason_list = []
        if not has_degree: reason_list.append("No B.Tech/Engineering")
        if len(res["skills"]) < 2: reason_list.append("Minimal Skills")
        res["reason"] = "Rejected: " + " & ".join(reason_list)
    
    return res
