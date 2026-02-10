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
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (name TEXT, score INTEGER, education TEXT, notice TEXT, skills TEXT)''')
    conn.commit()
    conn.close()

def save_candidate(name, score, education, notice, skills):
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?)", (name, score, education, notice, skills))
    conn.commit()
    conn.close()

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        # 1GB file optimization: Only first 3 pages
        pages_to_read = min(len(pdf_reader.pages), 3)
        for i in range(pages_to_read):
            content = pdf_reader.pages[i].extract_text()
            if content:
                text += content + " "
        
        # AGAR TEXT NAHI MILA (SCANNED PDF CASE): OCR START KAREIN
        if len(text.strip()) < 50:
            file.seek(0)
            images = convert_from_bytes(file.read(), first_page=1, last_page=2)
            for img in images:
                text += pytesseract.image_to_string(img)
        
        return re.sub(r'\s+', ' ', text).strip()
    except Exception as e:
        return ""

def analyze_resume(text):
    res = {"education": "Other", "notice_period": "90 Days (Standard)", "skills": [], "score": 25}
    if not text: return res

    # B.TECH & EDUCATION DETECTION
    edu_patterns = [r'B\.?\s*T\s*e\s*c\s*h', r'Bachelor\s*of\s*Technology', r'Engineering', r'Techno India']
    for pattern in edu_patterns:
        if re.search(pattern, text, re.I):
            res["education"] = "Technical Degree (India)"
            res["score"] += 45
            break

    # SKILLS DETECTION (Lucky's Stack Included)
    skill_list = ["Python", "Java", "PHP", "MySQL", "JavaScript", "HTML", "CSS", "Node", "Git", "Bootstrap"]
    for skill in skill_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.I):
            res["skills"].append(skill)
            res["score"] += 5
            
    res["score"] = min(res["score"], 100)
    return res
