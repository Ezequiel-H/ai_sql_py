# ai_sql_py

## Setup Instructions

To set up and run `ai_sql_py`, follow these steps:

### Prerequisites

- Ensure you have Python 3.9+ installed on your system.
- Ensure you have Docker and Docker Compose installed.

### Steps

#### 1. Populate the Database

Before starting the Docker container, populate the SQLite database by following these steps:

1. **Set Up a Virtual Environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**  
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare the Database**  
   Run the `data2db.py` script to populate the SQLite database:
   ```bash
   python data2db.py
   ```

   - Ensure `data.csv` exists in the project directory.
   - This script will create a SQLite database file named `database.db` and populate it with data from `data.csv`.

#### 2. Build and Run the Docker Container

Use Docker Compose to build and run the application:

```bash
docker-compose up --build
```

- This will build the Docker image defined in the `Dockerfile` and start the Flask application on port `5001`.

#### 3. Access the Application

Once the container is running, access the application in your browser or via an API client at:
```
http://localhost:5001
```

#### 4. Stop the Application

To stop the running containers:
```bash
docker-compose down
```

## API Documentation

### /nl-to-sql
Method: POST
Converts a natural language question into SQL, executes it, and returns the query, result, and explanation.

#### Request
Body:

question (String, required): The input question.

#### Example:

{
  "question": "What is the total revenue for the last quarter?"
}

