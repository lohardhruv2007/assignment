import streamlit as st
import pandas as pd
import sqlite3
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Recruiter Portal", layout="wide")

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            score INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>

/* Hide Streamlit default menu */
header, footer, #MainMenu {
    visibility: hidden;
}

/* App background */
.stApp {
    background-color: #f3f7f0;
    font-family: 'Times New Roman', serif;
}

/* Center content */
.main .block-container {
    padding-top: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

/* Title */
.title {
    font-size: 60px;
    font-weight: 800;
    color: #1b3022;
    margin-bottom: 50px;
}

/* Remove internal baseweb layers */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Remove password eye icon */
button[title="Show password"],
button[title="Hide password"] {
    display: none !important;
}

/* Input width */
[data-testid="stTextInput"] {
    width: 650px !important;
}

/* Input box style */
[data-testid="stTextInput"] > div {
    background: white !important;
    border: 3px solid #c8d6cc !important;
    border-radius: 18px !important;
    height: 75px !important;
    display: flex;
    align-items: center;
    padding: 0 20px;
}

/* Typing field */
[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    font-size: 26px !important;
    color: #6fa88f !important;
    text-align: center;
    width: 100%;
}

/* Focus border */
[data-testid="stTextInput"] > div:focus-within {
    border: 3px solid #4f6d5a !important;
}

/* Button style */
.stButton > button {
    width: 650px;
    height: 75px;
    background-color: #4f6d5a;
    color: white;
    font-size: 24px;
    font-weight: bold;
    border-radius: 18px;
    border: none;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN PAGE ----------------
if not st.session_state.logged_in:

    st.markdown('<div class="title">Recruiter Portal</div>', unsafe_allow_html=True)

    username = st.text_input("", placeholder="admin")
    password = st.text_input("", type="password", placeholder="hr123")

    if st.button("ENTER DASHBOARD"):
        if username == "admin" and password == "hr123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ---------------- DASHBOARD ----------------
else:

    st.markdown('<div class="title">Dashboard</div>', unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.write("Welcome to Recruiter Dashboard ✅")

    conn = sqlite3.connect("candidates.db")
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No candidates yet.")
