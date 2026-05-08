import PyPDF2
import re
import sqlite3

def init_db():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
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
        text = "".join([page.extract_text() + " " for page in pdf_reader.pages])
        return text.strip()
    except:
        return ""

def analyze_resume(text):
    res = {"education": "Other", "notice_period": "Immediate", "skills": [], "score": 20, "reason": "Review Required"}
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Engineering|Technology', text, re.I):
        res["education"] = "B.Tech Graduate"
        res["score"] += 40
    tech_skills = ["Python", "Java", "SQL", "React", "C++", "JavaScript", "Node", "AWS"]
    found = [s for s in tech_skills if re.search(r'\b' + re.escape(s) + r'\b', text, re.I)]
    res["skills"] = found
    res["score"] += (len(found) * 10)
    res["score"] = min(res["score"], 100)
    res["reason"] = "Shortlisted" if res["score"] >= 70 else "Rejected"
    return res
