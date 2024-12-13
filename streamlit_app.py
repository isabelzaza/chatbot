import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
import json
import requests
from PyPDF2 import PdfReader
import io

# Configure page
st.set_page_config(page_title="Psychology Dept. Teaching Inventory", layout="wide")

# Initialize session state variables if they don't exist
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'welcome'
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'uploaded_files_content' not in st.session_state:
    st.session_state.uploaded_files_content = ""

def amplify_chat(prompt, content=""):
    """Make a call to Amplify API with proper error handling"""
    url = "https://prod-api.vanderbilt.ai/chat"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "data": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 500,
            "dataSources": [],
            "assistantId": st.secrets["AMPLIFY_ASSISTANT_ID"],
            "options": {
                "ragOnly": False,
                "skipRag": True,
                "prompt": f"Context: {content}\n\nQuestion: {prompt}"
            }
        }
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(payload),
            auth=(st.secrets["AMPLIFY_API_KEY"], '')
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Amplify API: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def save_to_google_sheets(answers):
    """Save answers to Google Sheets"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"]),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(credentials)
        sheet = client.open_by_url(
            "https://docs.google.com/spreadsheets/d/1SaIoxcZ5AmMl0NiTKyGvG247RcKjJYoJ9QuUgalbSSQ/edit?gid=0"
        ).sheet1
        
        # Format answers into a row
        row = [answers.get(f'Q{i}', '') for i in range(1, 53)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {str(e)}")
        return False

# Welcome screen and file upload
if st.session_state.current_step == 'welcome':
    st.title("Psychology Department Teaching Inventory")
    st.write("""
    The full inventory has several questions but I want to help you answer them as fast as possible. 
    If you have a syllabus for the course, or any other document relevant to your teaching practices 
    in this course, please upload it.
    """)
    
    uploaded_files = st.file_uploader(
        "Upload your syllabus or other relevant documents", 
        accept_multiple_files=True,
        type=['pdf', 'txt']
    )
    
    if st.button("Continue"):
        if uploaded_files:
            # Process uploaded files
            for file in uploaded_files:
                if file.type == "application/pdf":
                    st.session_state.uploaded_files_content += extract_text_from_pdf(file)
                else:
                    st.session_state.uploaded_files_content += str(file.read(), 'utf-8')
            
            # Use Amplify to extract initial answers
            if st.session_state.uploaded_files_content:
                with st.spinner("Analyzing uploaded documents..."):
                    for i in range(1, 53):
                        response = amplify_chat(
                            f"Based on the provided document, what is the answer to Q{i}? "
                            "Respond with just the answer, no explanation.",
                            st.session_state.uploaded_files_content
                        )
                        if response and 'message' in response:
                            st.session_state.answers[f'Q{i}'] = response['message']
        
        st.session_state.current_step = 'questions'
        st.rerun()

# Questions screen
elif st.session_state.current_step == 'questions':
    st.title("Course Information")
    
    # Group questions by section
    sections = {
        "I: Course Details": range(1, 5),
        "II: Information Provided to Students": range(5, 9),
        "III: Supporting Materials": range(9, 20),
        "IV: In-Class Features": range(20, 29),
        "V: Assignments": range(29, 34),
        "VI: Feedback and Testing": range(34, 40),
        "VII: Other": range(40, 45),
        "VIII: TAs and LAs": range(45, 48),
        "IX: Collaboration": range(48, 53)
    }
    
    for section, q_range in sections.items():
        st.header(f"Section {section}")
        for i in q_range:
            if f'Q{i}' not in st.session_state.answers:
                st.session_state.answers[f'Q{i}'] = ""
            
            if i in [21, 22]:  # Percentage questions
                st.session_state.answers[f'Q{i}'] = st.slider(
                    f"Q{i}", 0, 100, 
                    int(st.session_state.answers[f'Q{i}']) if st.session_state.answers[f'Q{i}'] else 0
                )
            elif i == 23:  # Duration question
                st.session_state.answers[f'Q{i}'] = st.number_input(
                    f"Q{i}", 0, 180,
                    int(st.session_state.answers[f'Q{i}']) if st.session_state.answers[f'Q{i}'] else 0
                )
            elif i in [24, 26, 27, 28]:  # Frequency questions
                st.session_state.answers[f'Q{i}'] = st.selectbox(
                    f"Q{i}",
                    ['every class', 'every week', 'once in a while', 'rarely'],
                    index=['every class', 'every week', 'once in a while', 'rarely'].index(
                        st.session_state.answers[f'Q{i}']
                    ) if st.session_state.answers[f'Q{i}'] in ['every class', 'every week', 'once in a while', 'rarely'] else 0
                )
            elif i == 44:  # Often/sometimes/rarely question
                st.session_state.answers[f'Q{i}'] = st.selectbox(
                    f"Q{i}",
                    ['often', 'sometimes', 'rarely'],
                    index=['often', 'sometimes', 'rarely'].index(
                        st.session_state.answers[f'Q{i}']
                    ) if st.session_state.answers[f'Q{i}'] in ['often', 'sometimes', 'rarely'] else 0
                )
            else:  # Yes/No questions
                st.session_state.answers[f'Q{i}'] = st.selectbox(
                    f"Q{i}",
                    ['y', 'n'],
                    index=['y', 'n'].index(
                        st.session_state.answers[f'Q{i}'].lower()
                    ) if st.session_state.answers[f'Q{i}'].lower() in ['y', 'n'] else 0
                )
    
    if st.button("Submit"):
        # Save to Google Sheets
        if save_to_google_sheets(st.session_state.answers):
            # Generate feedback about missing information in syllabus
            missing_info = []
            for q in range(5, 20):  # Questions about syllabus content
                if f'Q{q}' not in st.session_state.uploaded_files_content:
                    missing_info.append(f'Q{q}')
            
            feedback_prompt = f"""
            Based on the following questions that couldn't be answered from the syllabus: {missing_info},
            provide a brief, friendly suggestion about what additional information could be included in 
            future syllabi. Keep the response under 3 sentences.
            """
            
            feedback_response = amplify_chat(feedback_prompt)
            
            st.success("Thank you for completing the inventory!")
            if feedback_response and 'message' in feedback_response:
                st.info(feedback_response['message'])
            
            # Reset session state for new submission
            st.session_state.current_step = 'welcome'
            st.session_state.answers = {}
            st.session_state.uploaded_files_content = ""
            st.rerun()