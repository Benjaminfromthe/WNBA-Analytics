import os
import threading
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from groq import Groq

# ==========================================
# 1. BACKGROUND SCHEDULER INITIALIZATION
# ==========================================
@st.cache_resource
def start_background_scheduler():
    """
    Launches scheduler.py in a background thread so the ETL pipeline 
    runs continuously in the cloud alongside Streamlit.
    """
    def run_scheduler():
        try:
            print("🚀 [Streamlit Thread] Starting background ETL scheduler...")
            import scheduler
        except Exception as e:
            print(f"❌ [Streamlit Thread] Error running background scheduler: {e}")

    # Create and start a daemon thread
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread

# Start the background ETL job once
start_background_scheduler()


# ==========================================
# 2. STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="WNBA Analytics AI Platform", 
    page_icon="🏀", 
    layout="wide"
)

st.title("🏀 WNBA Analytics & AI Insights Platform")
st.caption("Automated Cloud ETL Pipeline, Real-Time Supabase Data Sync & Conversational AI Assistant")

st.divider()

# ==========================================
# 3. LIVE DATABASE PREVIEW & METRICS
# ==========================================
st.subheader("📊 Live ETL Data & System Metrics")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")
DB_NAME = os.getenv("DB_NAME", "postgres")

if DB_HOST and DB_USER and DB_PASSWORD:
    try:
        # Construct PostgreSQL / Supabase connection URL
        db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_url)
        
        # Pull total row count and recent records
        df_count = pd.read_sql("SELECT COUNT(*) as total FROM wnba_games_raw", engine)
        df_preview = pd.read_sql("SELECT * FROM wnba_games_raw LIMIT 5", engine)
        
        total_rows = df_count["total"].iloc[0]

        # Display Top Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Database Status", "Connected 🟢")
        col2.metric("Total Ingested Records", f"{total_rows:,}")
        col3.metric("ETL Refresh Interval", "15 Mins")

        st.markdown("#### **Staging Data Preview (`wnba_games_raw`)**")
        st.dataframe(df_preview, use_container_width=True)
        st.success("Connected to Supabase PostgreSQL database successfully!")

    except Exception as e:
        st.warning(f"Could not load live database preview: {e}")
else:
    st.info("Database credentials missing or incomplete in environment variables.")

st.divider()

# ==========================================
# 4. INTERACTIVE GROQ AI ASSISTANT (WITH MEMORY)
# ==========================================
st.subheader("💬 Ask WNBA AI Assistant")

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("Missing GROQ_API_KEY environment variable. Please check Railway settings.")
else:
    try:
        # Initialize Groq Client
        client = Groq(api_key=groq_api_key)

        # Maintain chat session state across user inputs
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Render previous conversation history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # User chat input prompt box
        if prompt := st.chat_input("Ask about recent WNBA player stats, ETL status, or predictions..."):
            # Display user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Build conversational history payload for Groq
            groq_payload = [
                {
                    "role": "system",
                    "content": "You are a professional WNBA sports analytics expert and data engineer assistant. "
                               "Maintain full conversational context and answer queries accurately, concisely, and clearly."
                }
            ]

            # Append previous message memory
            for m in st.session_state.messages:
                groq_payload.append({
                    "role": m["role"],
                    "content": m["content"]
                })

            # Query Groq LLM (Llama 3.3 70B Versatile)
            try:
                chat_completion = client.chat.completions.create(
                    messages=groq_payload,
                    model="llama-3.3-70b-versatile",
                )
                reply = chat_completion.choices[0].message.content
            except Exception as err:
                reply = f"Error generating AI response: {err}"

            # Display AI message
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as setup_err:
        st.error(f"Failed to initialize Groq AI Client: {setup_err}")