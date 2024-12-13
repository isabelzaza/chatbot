import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
import io

# Configure page
st.set_page_config(page_title="Psychology Dept. Teaching Inventory - Simple", layout="wide")

# Define just the first 5 questions
QUESTIONS = {
    "Q1": "Instructor Name:",
    "Q2": "Course Number:",
    "Q3": "Semester and Year:",
    "Q4": "Number of Students:",
    "Q5": "Do you give students a list of the topics that will be covered in the course?"
}

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def amplify_chat(prompt, content=""):
    """Make a call to Amplify API with proper error handling"""
    url = "https://prod-api.vanderbilt.ai/chat"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.secrets["AMPLIFY_API_KEY"]}'
    }
    
    payload = {
        "data": {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant analyzing course documents."
                },
                {
                    "role": "user",
                    "content": f"Context: {content}\n\nQuestion: {prompt}"
                }
            ],
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 500,
            "assistant_id": st.secrets["AMPLIFY_ASSISTANT_ID"]
        }
    }
    
    try:
        # Debug: Print the payload structure
        st.write("Sending payload:", json.dumps(payload, indent=2))
        
        response = requests.post(
            url, 
            headers=headers, 
            json=payload
        )
        
        # Debug: Print response status and content
        st.write("Response status:", response.status_code)
        st.write("Response content:", response.text)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Amplify API: {str(e)}")
        return None

def analyze_syllabus(content):
    """Analyze syllabus content for first 5 questions"""
    prompt = """
    Analyze this course document and answer the following questions. For each question, 
    respond only with the answer (no explanation). If you're not certain, respond with 'Unknown':
    """
    
    answers = {}
    with st.spinner("Analyzing uploaded documents..."):
        for i in range(1, 6):
            specific_prompt = f"{prompt}\n\nQuestion: {QUESTIONS[f'Q{i}']}"
            response = amplify_chat(specific_prompt, content)
            
            if response and 'message' in response:
                answer = response['message'].strip()
                answers[f'Q{i}'] = answer
                st.write(f"{QUESTIONS[f'Q{i}']} {answer}")

def main():
    st.title("Psychology Department Teaching Inventory - Simple Version")
    st.write("Please upload your syllabus or other relevant documents.")
    
    uploaded_file = st.file_uploader(
        "Upload document",
        type=['pdf', 'txt']
    )
    
    if uploaded_file is not None:
        if st.button("Analyze Document"):
            content = ""
            if uploaded_file.type == "application/pdf":
                content = extract_text_from_pdf(uploaded_file)
            else:
                content = str(uploaded_file.read(), 'utf-8')
            
            if content:
                analyze_syllabus(content)

if __name__ == "__main__":
    main()