import streamlit as st

# This tells the app to pull the key securely from Streamlit's hidden vault
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-3.6-flash"

def is_api_key_configured():
    return len(GEMINI_API_KEY.strip()) > 20

#"/home/garvit7737/c language/.venv/bin/python3" -m streamlit run app.py