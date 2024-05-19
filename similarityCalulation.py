from flask import Flask, request, jsonify, send_file
import psycopg2
from flask_cors import CORS
import tempfile

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Function to fetch data from the database
def fetch_data_from_db():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        dbname="postgres",
        user="admin1",
        password="123",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    
    # Execute query to fetch data
    cur.execute("SELECT id, Education, Education_dates, Experience, Experience_dates, Skills, PDF_data FROM candidates")
    
    # Fetch all rows from the executed query
    rows = cur.fetchall()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    return rows

# Function to process fetched data into lists and vectors
def process_data(row):
    education_vector = row[1]
    education_dates_vector = row[2]
    experience_vector = row[3]
    experience_dates_vector = row[4]
    skills_vector = row[5]
    pdf_data = row[6]  # Retrieve PDF data
    return education_vector, education_dates_vector, experience_vector, experience_dates_vector, skills_vector, pdf_data

# Route to receive query list from frontend
@app.route('/process_query', methods=['POST'])
def process_query():
    data = request.get_json()
    query_list = data['resultList']  # Directly access 'resultList' key
    rows = fetch_data_from_db()
    
    # Placeholder for your similarity calculation logic
    # For now, assume you return the top 5 most similar candidate IDs
    results = {row[0]: 0 for row in rows}  # Replace with actual similarity logic
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    top_5_results = sorted_results[:5]
    
    # Return only the candidate IDs and their PDF links
    response_data = []
    for candidate_id, _ in top_5_results:
        response_data.append({
            "id": candidate_id,
            "pdf_link": f"http://127.0.0.1:5000/get_cv/{candidate_id}"
        })
    
    return jsonify(response_data)

# Route to retrieve and render PDF file
@app.route('/get_cv/<int:candidate_id>', methods=['GET'])
def get_cv(candidate_id):
    # Fetch data for the candidate from the database
    conn = psycopg2.connect(
        dbname="postgres",
        user="admin1",
        password="123",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT PDF_data FROM candidates WHERE id=%s", (candidate_id,))
    pdf_data = cur.fetchone()[0]
    cur.close()
    conn.close()

    # Create a temporary file to store the PDF data
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(pdf_data)
        tmp_file.seek(0)

        # Send the PDF file to the frontend for rendering
        return send_file(tmp_file.name, as_attachment=False, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
