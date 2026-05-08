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
    """AI logic to rank B.Tech resumes"""
    res = {"education": "Non-Tech", "notice_period": "Immediate", "skills": [], "score": 10, "reason": "Low Match"}
    
    # 1. Degree Detection
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor|Engineering|CS|IT', text, re.I):
        res["education"] = "B.Tech/BE"
        res["score"] += 40
    
    # 2. Skill Extraction (AI Keyword Matching)
    tech_stack = ["Python", "Java", "SQL", "React", "C\+\+", "JavaScript", "Node", "AWS", "Machine Learning"]
    found = [s.replace('\\', '') for s in tech_stack if re.search(r'\b' + s + r'\b', text, re.I)]
    res["skills"] = found
    res["score"] += (len(found) * 10)
    
    # 3. Final Ranking
    res["score"] = min(res["score"], 100)
    if res["score"] >= 75:
        res["reason"] = "Top Tier Candidate"
    elif res["score"] >= 45:
        res["reason"] = "Shortlisted for Interview"
    else:
        res["reason"] = "Does not meet criteria"
        
    return res
