import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from ai_assistant import execute_sql_query, ask_ai_assistant

# Sample data cleaning mock function for testing
def clean_wnba_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Utility function to clean raw WNBA data."""
    df_clean = df.drop_duplicates().copy()
    df_clean = df_clean.dropna(subset=['game_id', 'home_team'])
    return df_clean

# ----------------------------------------------------
# 1. Automated Tests for Data Cleaning & Schema Checks
# ----------------------------------------------------

def test_data_cleaning_deduplication():
    """Test that duplicate rows are removed during ETL transformation."""
    raw_data = pd.DataFrame({
        'game_id': [1, 1, 2],
        'home_team': ['Dallas Wings', 'Dallas Wings', 'Las Vegas Aces'],
        'pts_total': [160, 160, 175]
    })
    
    cleaned = clean_wnba_dataframe(raw_data)
    assert len(cleaned) == 2, "Duplicates should be removed during cleaning"

def test_data_cleaning_null_handling():
    """Test that invalid null keys are dropped."""
    raw_data = pd.DataFrame({
        'game_id': [1, None, 3],
        'home_team': ['Connecticut Sun', 'Atlanta Dream', 'Minnesota Lynx'],
        'pts_total': [150, 140, 165]
    })
    
    cleaned = clean_wnba_dataframe(raw_data)
    assert len(cleaned) == 2, "Rows with missing game_id should be dropped"


# ----------------------------------------------------
# 2. Automated Tests for AI Assistant & Error Handling
# ----------------------------------------------------

def test_sql_execution_security_check():
    """Test that non-SELECT statements are rejected for security."""
    invalid_sql = "DELETE FROM wnba_analytics_view;"
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        execute_sql_query(invalid_sql)

@patch('ai_assistant.get_groq_client')
def test_ai_assistant_valid_question(mock_groq):
    """Test that a standard question produces a valid pipeline answer."""
    # Mock SQL generation response
    mock_sql_response = MagicMock()
    mock_sql_response.choices[0].message.content = "SELECT home_team FROM wnba_analytics_view ORDER BY pts_total DESC LIMIT 1;"
    
    # Mock English summary response
    mock_summary_response = MagicMock()
    mock_summary_response.choices[0].message.content = "Dallas Wings scored the most points."
    
    # Configure mock client behavior
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [mock_sql_response, mock_summary_response]
    mock_groq.return_value = mock_client

    with patch('ai_assistant.execute_sql_query') as mock_exec:
        mock_exec.return_value = pd.DataFrame({'home_team': ['Dallas Wings']})
        
        answer = ask_ai_assistant("Which team scored the most points?")
        
        assert "Dallas Wings" in answer
        assert mock_exec.called

def test_ai_assistant_invalid_question_no_crash():
    """Test that an unanswerable or broken question handles errors gracefully without crashing."""
    # Force an unparseable input / error scenario
    with patch('ai_assistant.generate_sql_query', side_effect=Exception("Database syntax error")):
        response = ask_ai_assistant("Blah blah gibberish unsupported question???")
        
        # Verify the program catches the error and returns a friendly message instead of raising an exception
        assert "I'm sorry, I couldn't process that question" in response