import os
import re
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from groq import Groq

# Load environment variables
load_dotenv()

# Setup PostgreSQL Database Connection
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "wnba_bigdata_db")

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# Table schema details for LLM prompt context
TABLE_SCHEMA = """
Table View Name: wnba_analytics_view
Columns:
 - game_id (INTEGER)
 - season (INTEGER)
 - home_team (VARCHAR/TEXT) -> e.g. 'Connecticut Sun', 'New York Liberty', 'Dallas Wings', 'Las Vegas Aces', 'Minnesota Lynx', 'Atlanta Dream'
 - visitor_team (VARCHAR/TEXT)
 - home_team_score (INTEGER)
 - visitor_team_score (INTEGER)
 - pts_total (INTEGER)
 - point_diff (INTEGER)
 - home_win (INTEGER) -> 1 if home team won, 0 otherwise
 - field_goal_pct (NUMERIC/FLOAT)
 - turnovers (INTEGER)
"""

def get_groq_client():
    """Initialize Groq API client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
    return Groq(api_key=api_key)

def generate_sql_query(user_question: str) -> str:
    """Step 1: AI turns plain-English question into SQL query."""
    client = get_groq_client()
    
    system_prompt = (
        "You are an expert PostgreSQL developer. Convert the user's question about WNBA game data "
        "into a valid PostgreSQL SQL query using ONLY the view `wnba_analytics_view`.\n"
        f"{TABLE_SCHEMA}\n"
        "STRICT RULES:\n"
        "1. Return ONLY the raw SQL query. Do NOT use markdown code blocks, do NOT add explanations.\n"
        "2. Ensure table name is `wnba_analytics_view`.\n"
        "3. Keep queries read-only (SELECT statements only)."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.0
    )
    
    sql_query = response.choices[0].message.content.strip()
    # Clean up any residual markdown formatting if returned
    sql_query = re.sub(r"```sql|```", "", sql_query).strip()
    return sql_query

def execute_sql_query(sql_query: str):
    """Step 2: Run SQL query against PostgreSQL database and handle errors."""
    if not sql_query.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed for security.")

    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        rows = result.fetchall()
        columns = result.keys()
        
    df_result = pd.DataFrame(rows, columns=columns)
    return df_result

def summarize_result(user_question: str, sql_query: str, query_result: pd.DataFrame) -> str:
    """Step 3: AI turns SQL results into a friendly plain-English response."""
    client = get_groq_client()
    
    result_str = query_result.to_string(index=False) if not query_result.empty else "No matching records found."
    
    system_prompt = (
        "You are a helpful sports analytics AI assistant for WNBA statistics. "
        "Given the user's question, the executed SQL query, and the SQL output result, "
        "provide a concise, natural, plain-English summary answer."
    )

    user_prompt = (
        f"Question: {user_question}\n"
        f"Executed SQL: {sql_query}\n"
        f"Data Result:\n{result_str}\n\n"
        "Provide a clear, plain-English answer:"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content.strip()

def ask_ai_assistant(user_question: str) -> str:
    """Complete End-to-End AI Assistant Workflow with Robust Error Handling."""
    print(f"\n[User Question]: {user_question}")
    try:
        # Step 1: Text-to-SQL
        sql_query = generate_sql_query(user_question)
        print(f"[Generated SQL]: {sql_query}")
        
        # Step 2: Execute Query
        df_result = execute_sql_query(sql_query)
        
        # Step 3: SQL Result to Plain English
        answer = summarize_result(user_question, sql_query, df_result)
        return answer

    except Exception as e:
        # Robust Error Handling (Requirement 4.5)
        error_msg = f"I'm sorry, I couldn't process that question. Error details: {str(e)}"
        print(f"[Error Handled]: {error_msg}")
        return error_msg

if __name__ == "__main__":
    print("=" * 60)
    print("WNBA AI ASSISTANT (Powered by Groq API & PostgreSQL)")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 60)
    
    while True:
        question = input("\nAsk a question about WNBA analytics (e.g. 'Which team scored the most points in 2024?'): ").strip()
        if question.lower() in ['exit', 'quit']:
            break
        if not question:
            continue
        
        answer = ask_ai_assistant(question)
        print(f"\n[AI Answer]:\n{answer}")