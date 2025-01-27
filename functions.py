import sqlite3
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# SQLite Database Configuration
table_name = "sales"
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# OpenAI API Calls
def call_openai_chat_model(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content

# Fetch table schema
def get_table_schema():
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    schema = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
    schema_str = ", ".join([f"{col['name']} ({col['type']})" for col in schema])
    return schema_str

# Natural language to SQL
def translate_to_sql(natural_query):
    schema = get_table_schema()
    prompt = f"""
### Task:
Write only the SQL query to answer the following question based on the provided database schema.

### Database:
The database is called '{table_name}' and has the following schema:
{schema}

### Question:
{natural_query}

### Example:
Your response format should only be:
SELECT week_day, SUM(total) AS total_sales FROM sales GROUP BY week_day ORDER BY total_sales DESC LIMIT 1;
Without any additional text or special characters.
"""

    return call_openai_chat_model(prompt)

# Run SQL query
def execute_query(query):
    try:
        # Execute the query
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return None

# Generate NL Response
def get_nl_response(question, sql_query, query_result):
    prompt = f"""
Given the following inputs, generate a clear and concise natural language response:

1. Question: {question}
2. SQL Query: {sql_query}
3. Query Result: {query_result}

If `query_result` contains data:
- Summarize the result in a user-friendly way.
- Relate it back to the `question`.
- Add appropriate units to the values if applicable (e.g., use '$' for monetary values, '%' for percentages, or any relevant unit).
- Ensure the response is clear and concise.

If `query_result` is empty:
- Inform the user no data was found.

Response:
"""
    return call_openai_chat_model(prompt)

# Process natural language question
def process_nl_question(nl_input):
    if not nl_input:
        raise ValueError("Input is required")
   
    sql_query = translate_to_sql(nl_input)
    sql_query_result = execute_query(sql_query)
    nl_result = get_nl_response(nl_input, sql_query, sql_query_result)
    return sql_query, sql_query_result, nl_result
