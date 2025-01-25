from flask import Flask, jsonify, render_template, request
from functions import process_nl_question

app = Flask(__name__)

# /nl-to-sql NL Query to SQL Query, SQL Result and NL Result
@app.route('/nl-to-sql', methods=['POST'])
def translate():
    try:
        # Parse and validate input data.
        data = request.get_json()
        question = data.get("question")
        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Process the question and generate a response
        sql_query, sql_query_result, nl_result = process_nl_question(question)
        return jsonify({"sql_query": sql_query, "sql_query_result": sql_query_result, "nl_result": nl_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Page for user entered NL Query to SQL Query, SQL Result and NL Result
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            nl_question = request.form.get('nl_question')
            sql_query, sql_query_result, nl_result = process_nl_question(nl_question)
            return render_template('result.html', nl_question=nl_question, sql_query=sql_query, sql_query_result=sql_query_result, nl_result=nl_result)
        except Exception as e:
            return render_template('error.html', error=str(e))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
