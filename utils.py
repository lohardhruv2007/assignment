import PyPDF2
import re
import sqlite3

def init_db():
    """Naya Database banata hai"""
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
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content: text += content + " "
        return text.strip()
    except Exception:
        return ""

def analyze_resume(text):
    # Specialized for B.Tech/Engineering students
    res = {"education": "Non-Tech", "notice_period": "90 Days", "skills": [], "score": 20, "reason": "Rejected"}
    
    # Degree Search
    if re.search(r'B\.?\s*T\s*e\s*c\s*h|Bachelor\s*of\s*Technology|Engineering', text, re.I):
        res["education"] = "B.Tech/Engineering"
        res["score"] += 50
        
    # Skills Search
    tech_skills = ["Python", "Java", "SQL", "React", "C++", "JavaScript", "PHP", "MySQL"]
    found = [s for s in tech_skills if re.search(r'\b' + re.escape(s) + r'\b', text, re.I)]
    res["skills"] = found
    res["score"] += (len(found) * 10)
    res["score"] = min(res["score"], 100)
    
    if res["score"] >= 70: res["reason"] = "Highly Recommended"
    elif res["score"] >= 40: res["reason"] = "Waitlisted"
    
    return res
