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
    # Naya schema: 'reason' column ke saath
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (name TEXT, score INTEGER, education TEXT, notice TEXT, skills TEXT, reason TEXT)''')
    conn.commit()
    conn.close()

def save_candidate(name, score, education, notice, skills, reason):
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?)", (name, score, education, notice, skills, reason))
    conn.commit()
    conn.close()

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        # Large file handling: Only first 3 pages
        pages_to_read = min(len(pdf_reader.pages), 3)
        for i in range(pages_to_read):
            content = pdf_reader.pages[i].extract_text()
            if content:
                text += content + " "
        
        # AGAR TEXT NAHI MILA (Lucky's Scanned PDF Case): OCR START KAREIN
        if len(text.strip()) < 50:
            file.seek(0)
            images = convert_from_bytes(file.read(), first_page=1, last_page=2)
            for img in images:
                text += pytesseract.image_to_string(img)
        
        # Table/Column gap cleaning
        return re.sub(r'\s+', ' ', text).strip()
    except Exception as e:
        return ""

def analyze_resume(text):
    res = {"education": "Other", "notice_period": "90 Days (Standard)", "skills": [], "score": 25, "reason": ""}
    if not text: 
        res["reason"] = "Rejected: Scanned content unreadable or empty file."
        return res

    # 1. Flexible Education Detection
    has_degree = False
    edu_patterns = [r'B\.?\s*T\s*e\s*c\s*h', r'Bachelor\s*of\s*Technology', r'Engineering', r'Techno India']
    for pattern in edu_patterns:
        if re.search(pattern, text, re.I):
            res["education"] = "Technical Degree (India)"
            res["score"] += 45
            has_degree = True
            break

    # 2. Skill Detection (Matching Lucky's Stack)
    skill_list = ["Python", "Java", "PHP", "MySQL", "JavaScript", "HTML", "CSS", "Node", "Git", "Bootstrap"]
    for skill in skill_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.I):
            res["skills"].append(skill)
            res["score"] += 5
            
    res["score"] = min(res["score"], 100)

    # 3. REASONING LOGIC (Selection/Rejection Feedback)
    if res["score"] >= 70:
        res["reason"] = f"Selected: Strong {res['education']} with core skills: {', '.join(res['skills'][:3])}."
    elif res["score"] >= 40:
        res["reason"] = "Waitlist: Technical degree found, but requires more specific skill matches."
    else:
        fail_reasons = []
        if not has_degree: fail_reasons.append("No Technical Degree (B.Tech)")
        if len(res["skills"]) < 2: fail_reasons.append("Low Skill Match")
        res["reason"] = "Rejected: " + " & ".join(fail_reasons)

    return res
