import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from docx import Document
from docx.text.hyperlink import Hyperlink
from PyPDF2 import PdfReader

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def summarize_note(resume_text:str,resume_headings:str):
    prompt = ("You are an helpful assistant. Your task is to parse a resume into JSON format."
              "Capitalize the key names appropriately, using _ in the place of spaces." 
              "The keys for link values should have an additional _link appended to their name."
              f"{f"Follow this set of headings: {resume_headings}" if resume_headings else ""}"
              f"The resume: {resume_text}")
    response = model.generate_content(prompt)
    result = response.text
    return result
    #return prompt

st.title("JSON Parser")
st.write("Upload your resume (docx preferred due to preserving links) or type it in and receive a parsed version in JSON.")

def extract_text_from_docx(file):
    document = Document(file)
    full_text = []
    for paragraph in document.paragraphs:
        paragraph_text = []
        for group in paragraph.iter_inner_content():
            if isinstance(group,Hyperlink):
                paragraph_text.append(group.text + "/" + group.address)
            else: #it is a run
                paragraph_text.append(group.text)
        full_text.append("".join(paragraph_text))
    return "\n".join(full_text)

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    full_text = [page.extract_text() for page in pdf_reader.pages]
    return "".join(full_text) # They get extracted with newlines by themselves

uploaded_file = st.file_uploader("Upload a file (.docx or .pdf)", type=["docx","pdf"])

if uploaded_file:
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = extract_text_from_docx(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
        resume_text = None
else:
    resume_text = st.text_area("Or, enter your resume here")

resume_headings = st.text_area("Enter resume headings here (optional)")

if (st.button("Convert to JSON")):
    if resume_text:
        summary = summarize_note(resume_text,resume_headings)
        st.subheader("JSON")
        st.write(summary)
    else:
        st.warning("Please enter a note into the text box")

