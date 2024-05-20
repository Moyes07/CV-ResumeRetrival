from flask import Flask, request, jsonify, send_file
import psycopg2
from flask_cors import CORS
import tempfile
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    query_list = data['resultList']  # Extract the list of queries directly without the 'resultList' key
    rows = fetch_data_from_db()


    response_data = []

    for query in query_list:
        skills = []
        experience = []
        education = []


        # Iterate through each parameter in the query
        for query in query_list:
            for param in query:
                category, value = param.split(':')
                if category.strip().lower() == 'skills':
                    skills.extend(value.split(','))
                elif category.strip().lower() == 'experience':
                    experience.extend(value.split(','))
                elif category.strip().lower() == 'education':
                    education.extend(value.split(','))

        # Extract text data from database rows
        candidate_texts = [(row[0],row[1], row[3], row[5]) for row in rows] 

        # Vectorize the query skills, experience, and education
        vectorizer = CountVectorizer().fit(skills + experience + education)
        skills_vector = vectorizer.transform(skills)
        experience_vector = vectorizer.transform(experience)
        education_vector = vectorizer.transform(education)

        similarities = []
        for candidate in candidate_texts:
            candidate_education = candidate[1]
            candidate_experience = candidate[2]
            candidate_skills = candidate[3]
            candidate_id = rows[candidate_texts.index(candidate)][0]

            candidate_education_similarity = cosine_similarity(education_vector, vectorizer.transform([candidate_education]))
            candidate_experience_similarity = cosine_similarity(experience_vector, vectorizer.transform([candidate_experience]))
            candidate_skills_similarity = cosine_similarity(skills_vector, vectorizer.transform([candidate_skills]))

            total_similarity = (candidate_education_similarity.mean() + candidate_experience_similarity.mean() + candidate_skills_similarity.mean())
            similarities.append((candidate_id, total_similarity))
            
        top_5_candidates = sorted(similarities, key=lambda x: x[1], reverse=True)[:5]

        # Add the top 5 candidates to the response data if similarity is greater than 0
        for candidate_id, similarity in top_5_candidates:
            if similarity > 0:
                cv_link = f"http://127.0.0.1:5000/get_cv/{candidate_id}"

                # Append the CV link along with other candidate information
        response_data.append({
            "id": candidate_id,
            "pdf_link": cv_link,
            "total_similarity": similarity
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
