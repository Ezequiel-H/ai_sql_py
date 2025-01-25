# functions funcionando con mal modelo

import sqlite3
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration, GPTNeoForCausalLM, GPT2Tokenizer

# SQLite Database Configuration
table_name = "sales"
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# SQL Model Configuration
sql_tokenizer = T5Tokenizer.from_pretrained('t5-small')
sql_model = T5ForConditionalGeneration.from_pretrained('cssupport/t5-small-awesome-text-to-sql')
sql_model = sql_model.to(device)
sql_model.eval()

# LLM Model Configuration
llm_model_name = "EleutherAI/gpt-neo-125M"
llm_model = GPTNeoForCausalLM.from_pretrained(llm_model_name)
llm_tokenizer = GPT2Tokenizer.from_pretrained(llm_model_name)

if llm_tokenizer.pad_token is None:
    llm_tokenizer.pad_token = llm_tokenizer.eos_token

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
### Task
Write an SQL query to answer the following question based on the provided database schema.

### Database
The database is called 'sales' and has the following schema:
{schema}

### Question
{natural_query}

### SQL Query
"""
    inputs = sql_tokenizer(prompt, padding=True, truncation=True, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = sql_model.generate(**inputs, max_length=512)
    generated_sql = sql_tokenizer.decode(outputs[0], skip_special_tokens=True)

    return generated_sql
    # return "SELECT week_day, SUM(total) AS total_revenue FROM sales GROUP BY week_day ORDER BY total_revenue DESC LIMIT 1;"

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

If `query_result` is empty:
- Inform the user no data was found.

Example Output:
"The day with the highest revenue is Monday, with a total of $1500.00."

Response:
"""
    inputs = llm_tokenizer(prompt, padding=True, truncation=True, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = llm_model.generate(**inputs, max_length=512)
    nl_response = llm_tokenizer.decode(outputs[0], skip_special_tokens=True)

    return nl_response
    # return "The best sales day was Friday, with a total revenue of $37,583,125."

# Process natural language question
def process_nl_question(nl_input):
    if not nl_input:
        raise ValueError("Input is required")
    sql_query = translate_to_sql(nl_input)
    sql_query_result = execute_query(sql_query)
    nl_result = get_nl_response(nl_input, sql_query, sql_query_result)
    return sql_query, sql_query_result, nl_result
