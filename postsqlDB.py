from readCV import edu_dates_regex,education_list_without_dates,exp_dates_regex,experience_list_without_dates,skills_set,edu_tenure_durations_str,exp_tenure_durations_str,pdf_path
import psycopg2


def read_pdf_file(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_data = file.read()
    return pdf_data

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="postgres",
    user="admin1",
    password="123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        ID SERIAL PRIMARY KEY,
        Education TEXT,
        Education_dates TEXT,
        Experience TEXT,
        Experience_dates TEXT,
        Skills TEXT,
        PDF_data BYTEA
    )
""")

# Read the PDF file
pdf_data = read_pdf_file(pdf_path)

# Prepare data for insertion
education_text = " | ".join(education_list_without_dates)
experience_text = " | ".join(experience_list_without_dates)
skills_text = ", ".join(skills_set)
edu_tenure_durations = " | ".join(edu_tenure_durations_str)
exp_tenure_durations = " , ".join(exp_tenure_durations_str)

# Insert data into table
cur.execute("""
    INSERT INTO candidates (Education, Education_dates, Experience, Experience_dates, Skills, PDF_data)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (education_text, edu_tenure_durations, experience_text, exp_tenure_durations, skills_text, pdf_data))

# Commit and close connection
conn.commit()
cur.close()
conn.close()

print("Data including the PDF file has been inserted into the database.")