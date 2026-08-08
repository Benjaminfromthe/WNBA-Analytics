import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from google import genai

# Page Configuration
st.set_page_config(page_title="WNBA Analytics AI", page_icon="🏀")
st.title("🏀 WNBA Analytics & AI Insights")

# 1. Quick Database Status View
st.subheader("📊 Live ETL Data Preview")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")
DB_NAME = os.getenv("DB_NAME", "postgres")

if DB_HOST:
    try:
        db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_url)
        df = pd.read_sql("SELECT * FROM wnba_games_raw LIMIT 5", engine)
        st.dataframe(df)
    except Exception as e:
        st.warning("Could not connect to database preview.")

# 2. Interactive AI Assistant
st.subheader("💬 Ask WNBA AI Assistant")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY environment variable.")
else:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about recent WNBA player performance or stats..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a WNBA analytics expert. Answer this request: {prompt}"
            )
            reply = response.text
        except Exception as err:
            reply = f"Error generating response: {err}"

        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})