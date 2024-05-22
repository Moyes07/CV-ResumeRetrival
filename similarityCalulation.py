from flask import Flask, request, jsonify, send_file
import psycopg2
from flask_cors import CORS
import tempfile
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


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

        print("Skills Vector:", skills_vector.toarray())
        print("Experience Vector:", experience_vector.toarray())
        print("Education Vector:", education_vector.toarray())

        similarities = []
        for candidate in candidate_texts:
            candidate_education = candidate[1]
            candidate_experience = candidate[2]
            candidate_skills = candidate[3]
            candidate_id = rows[candidate_texts.index(candidate)][0]
            
            candidate_skills_vector = vectorizer.transform([candidate_skills])
            candidate_experience_vector = vectorizer.transform([candidate_experience])
            candidate_education_vector = vectorizer.transform([candidate_education])


            skills_similarity = cosine_similarity(skills_vector, candidate_skills_vector)[0][0]
            experience_similarity = cosine_similarity(experience_vector, candidate_experience_vector)[0][0]
            education_similarity = cosine_similarity(education_vector, candidate_education_vector)[0][0]
    
            # Combine the similarities. Here, you can use a weighted average or simple average.
            overall_similarity = (skills_similarity + experience_similarity + education_similarity) / 3
    
            similarities.append((candidate_id, overall_similarity))

            print(f"Candidate ID: {candidate_id}")
            print("Candidate Skills Vector:", candidate_skills_vector.toarray())
            print("Candidate Experience Vector:", candidate_experience_vector.toarray())
            print("Candidate Education Vector:", candidate_education_vector.toarray())
            print(f"Skills Similarity: {skills_similarity}")
            print(f"Experience Similarity: {experience_similarity}")
            print(f"Education Similarity: {education_similarity}")
            print(f"Overall Similarity: {overall_similarity}")
            print("--------------------------------------")
            
        sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

        print("Sorted Similarities (Candidate ID, Skills Similarity, Experience Similarity, Education Similarity, Overall Similarity):")
        for sim in sorted_similarities:
            print(sim)

        # Add the top 3 candidates to the response data
        for candidate in sorted_similarities[:3]:
            candidate_id, overall_similarity = candidate
    
            # Create the CV link
            cv_link = f"http://127.0.0.1:5000/get_cv/{candidate_id}"

                # Append the CV link along with other candidate information
            response_data.append({
                "id": candidate_id,
                "pdf_link": cv_link,
                "total_similarity": overall_similarity,
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
