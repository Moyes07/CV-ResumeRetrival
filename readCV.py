import PyPDF2
import re
from datetime import datetime


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        for page_number in range(num_pages):
            page = reader.pages[page_number]
            text += page.extract_text()
    return text

# Function to extract sections from text using regex
def extract_sections(text):
    # Define regular expressions for each section header
    section_patterns = {
        "Education": r"(?i)education(?=.*BS)(.*?)(?=Experience)",
        "Experience": r"(?i)experience(.*?)(?=Skills)",
        "Skills": r"(?i)skills(.*?)(?=Projects)",
        "Projects": r"(?i)projects(.*?)(?=Interests)",
        "Interests and Extracurriculars": r"(?i)interests and extracurriculars(.*)"
        # Add more section patterns as needed
    }
    sections = {}

    for section, pattern in section_patterns.items():
        matches = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            sections[section] = matches.group(1).strip()
    
    return sections

# Extract text from the CV
pdf_path = "testcv4.pdf"  # Replace with the path to your PDF file
text = extract_text_from_pdf(pdf_path)

# Extract sections from the CV text
sections = extract_sections(text)

# Print extracted sections
for section, content in sections.items():
    print(section + ":\n" + content + "\n")


def process_section(section_text, section_type):
    # Split the text based on different criteria depending on the section type
    if section_type == "Education":
        items = [item.strip() for item in section_text.split('. ') if item.strip()]
    elif section_type == "Experience":
        items = [item.strip() for item in section_text.split('.') if item.strip()]
    elif section_type == "Skills":
        items = [item.strip() for item in section_text.split(',') if item.strip()]
    elif section_type in ["Projects", "Interests and Extracurriculars"]:
        items = []
        for item in section_text.split('•'):
            item = item.strip()
            if item:
                items.append(item)
    else:
        items = [item.strip() for item in section_text.split('\n') if item.strip()]
    
    return items

# Usage:
education_set = process_section(sections["Education"], "Education")
experience_set = process_section(sections["Experience"], "Experience")
skills_set = process_section(sections["Skills"], "Skills")
projects_set = process_section(sections["Projects"], "Projects")
interests_set = process_section(sections["Interests and Extracurriculars"], "Interests and Extracurriculars")

def extract_dates_with_regex(text_set):
    # Define the regular expression pattern to match date ranges
    date_pattern = r"(\d{1,2})/(\d{4}) – (\d{1,2})/(\d{4})|\d{1,2}/(\d{2}) - present|(\d{1,2})/(\d{4}) – Present"

    extracted_dates = []

    # Get the current month and year
    current_month = datetime.now().strftime("%m")
    current_year = datetime.now().strftime("%Y")

    # Iterate over each text in the set
    for text in text_set:
        # Use findall to search for date ranges
        matches = re.findall(date_pattern, text, re.IGNORECASE)
        
        # Process each match
        for match in matches:
            # Check if the match contains "Present"
            if match[3].lower() == "present":
                # If the second date is "Present", replace it with the current month and year
                date_range = f"{match[0]}/{match[1]} - {current_month}/{current_year}"
                extracted_dates.append(date_range)
            elif match[5]:  # If match contains MM/YY - present format
                start_month = match[5]
                start_year = match[6]
                date_range = f"{start_month}/{start_year} - {current_month}/{current_year}"
                extracted_dates.append(date_range)
            else:
                # Otherwise, add the date range as it is
                date_range = f"{match[0]}/{match[1]} - {match[2]}/{match[3]}"
                extracted_dates.append(date_range)

    return extracted_dates

# Extract dates from Education and Experience sets using the updated regular expression
edu_dates_regex = extract_dates_with_regex(education_set)
exp_dates_regex = extract_dates_with_regex(experience_set)

def remove_dates_with_regex(text_set):
    # Define the regular expression pattern to match date ranges
    date_pattern = r"(\d{1,2})/(\d{4}) – (\d{1,2})/(\d{4})|\d{1,2}/(\d{2}) - present|(\d{1,2})/(\d{4}) – Present"
    
    # Initialize an empty list to store the text without dates
    text_list_without_dates = []

    # Iterate over each text in the set
    for text in text_set:
        # Use sub to replace date patterns with an empty string
        text_without_dates = re.sub(date_pattern, "", text, flags=re.IGNORECASE)
        
        # Append the modified text to the list
        text_list_without_dates.append(text_without_dates.strip())

    return text_list_without_dates

# Remove dates from Education and Experience sets using regular expressions
education_list_without_dates = remove_dates_with_regex(list(education_set))
experience_list_without_dates = remove_dates_with_regex(list(experience_set))

def calculate_tenure_durations(date_ranges):
    tenure_durations = []
    for date_range in date_ranges:
        start_date, end_date = date_range.split(" - ")
        start_month, start_year = map(int, start_date.split("/"))
        end_month, end_year = map(int, end_date.split("/"))
        
        # Calculate tenure in months
        if start_year == end_year:
            duration = end_month - start_month + 1
        else:
            duration = (end_year - start_year) * 12 + (end_month - start_month) + 1
        tenure_durations.append(duration)
    
    return tenure_durations

# Calculate tenure durations for Education and Experience date ranges
edu_tenure_durations = calculate_tenure_durations(edu_dates_regex)
exp_tenure_durations = calculate_tenure_durations(exp_dates_regex)

# Convert integer durations to strings
edu_tenure_durations_str = " | ".join(map(str, edu_tenure_durations))
exp_tenure_durations_str = " | ".join(map(str, exp_tenure_durations))

# Print the tenure durations
print("Education Tenure Durations (in months):", edu_tenure_durations)
print("Experience Tenure Durations (in months):", exp_tenure_durations)


# Print extracted dates
print("\nEducation_dates (Regex):")
for date_range in edu_dates_regex:
    print(date_range)

print("\nExperience_dates (Regex):")
for date_range in exp_dates_regex:
    print(date_range)

# Print the updated sets without dates
print("\nEducation_set (Without Dates):")
for item in education_list_without_dates:
    print(item)

print("\nExperience_set (Without Dates):")
for item in experience_list_without_dates:
    print(item)

print("\nSkills_set:")
for item in skills_set:
    print(item)

print("\nProjects_set:")
for item in projects_set:
    print(item)

print("\nInterests and Extracurriculars_set:")
for item in interests_set:
    print(item)
