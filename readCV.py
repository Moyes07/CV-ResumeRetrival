import PyPDF2
import re
import spacy

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        for page_number in range(num_pages):
            page = reader.pages[page_number]
            text += page.extract_text()
    return text

def extract_entities(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    return entities

if __name__ == "__main__":
    pdf_path = "testcv1.pdf"  # Replace with the path to your PDF file
    text = extract_text_from_pdf(pdf_path)
    entities = extract_entities(text)

    # Print extracted named entities
    for label, entity_list in entities.items():
        print(f"{label}:")
        for entity in entity_list:
            print(entity)
        print("="*50)
