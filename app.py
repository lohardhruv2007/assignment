st.markdown("""
<style>

/* Remove baseweb layers */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Remove password eye toggle */
button[title="Show password"],
button[title="Hide password"] {
    display: none !important;
}

/* Input container */
[data-testid="stTextInput"],
[data-testid="stTextInput"] > div,
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] div {
    background: white !important;
    box-shadow: none !important;
}

/* Style main box */
[data-testid="stTextInput"] > div {
    border: 3px solid #c8d6cc !important;
    border-radius: 18px !important;
    height: 75px !important;
    width: 650px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 20px !important;
}

/* Actual typing field */
[data-testid="stTextInput"] input {
    border: none !important;
    outline: none !important;
    font-size: 26px !important;
    color: #6fa88f !important;
    text-align: center !important;
    width: 100% !important;
}

/* Focus */
[data-testid="stTextInput"] > div:focus-within {
    border: 3px solid #4f6d5a !important;
}

</style>
""", unsafe_allow_html=True)
