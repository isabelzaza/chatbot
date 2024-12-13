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

# Define questions dictionary
QUESTIONS = {
    "Q1": "Instructor Name:",
    "Q2": "Course Number:",
    "Q3": "Semester and Year:",
    "Q4": "Number of Students:",
    # [Rest of the questions dictionary remains the same]
}

# Initialize session state variables
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'welcome'
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'uploaded_files_content' not in st.session_state:
    st.session_state.uploaded_files_content = ""

def yes_no_buttons(key, question, pre_answered=False):
    """Create horizontal yes/no buttons with green background if pre-answered"""
    col1, col2, col3 = st.columns([10, 1, 1])
    
    with col1:
        if pre_answered:
            st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{question}</div>', unsafe_allow_html=True)
        else:
            st.write(question)
    
    with col2:
        yes_button = st.button('Yes', key=f'{key}_yes')
        if yes_button:
            st.session_state.answers[key] = 'y'
    
    with col3:
        no_button = st.button('No', key=f'{key}_no')
        if no_button:
            st.session_state.answers[key] = 'n'
    
    # Show current selection
    if key in st.session_state.answers:
        st.write(f"Selected: {'Yes' if st.session_state.answers[key] == 'y' else 'No'}")

def frequency_buttons(key, question, options, pre_answered=False):
    """Create horizontal frequency buttons"""
    col1, *option_cols = st.columns([10] + [1] * len(options))
    
    with col1:
        if pre_answered:
            st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{question}</div>', unsafe_allow_html=True)
        else:
            st.write(question)
    
    for option, col in zip(options, option_cols):
        with col:
            if st.button(option, key=f'{key}_{option}'):
                st.session_state.answers[key] = option
    
    # Show current selection
    if key in st.session_state.answers:
        st.write(f"Selected: {st.session_state.answers[key]}")

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

def analyze_syllabus(content):
    """Analyze syllabus content to extract answers"""
    prompt = f"""
    Analyze this course document and answer the following questions. For each question, respond only with 'y', 'n', or the specific requested value (no explanation):

    {content}

    For each question, look for explicit evidence in the document. Do not make assumptions. If you're not certain, respond with 'n'.
    """
    with st.spinner("Analyzing uploaded documents..."):
        for i in range(1, 53):
            specific_prompt = f"{prompt}\n\nQuestion: {QUESTIONS[f'Q{i}']}"
            response = amplify_chat(specific_prompt, content)
            if response and 'message' in response:
                st.session_state.answers[f'Q{i}'] = response['message'].strip().lower()
                # Debug info
                st.write(f"Q{i}: {response['message'].strip()}")

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
        
        row = [answers.get(f'Q{i}', '') for i in range(1, 53)]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {str(e)}")
        return False

# Main app flow
def main():
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
                for file in uploaded_files:
                    if file.type == "application/pdf":
                        st.session_state.uploaded_files_content += extract_text_from_pdf(file)
                    else:
                        st.session_state.uploaded_files_content += str(file.read(), 'utf-8')
                
                if st.session_state.uploaded_files_content:
                    analyze_syllabus(st.session_state.uploaded_files_content)
            
            st.session_state.current_step = 'questions'
            st.rerun()

    # Questions screen
    elif st.session_state.current_step == 'questions':
        st.title("Course Information")
        
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
                q_key = f'Q{i}'
                pre_answered = q_key in st.session_state.answers and st.session_state.answers[q_key] != ""
                
                if i in [21, 22]:  # Percentage questions
                    col1, col2 = st.columns([10, 2])
                    with col1:
                        if pre_answered:
                            st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{QUESTIONS[q_key]}</div>', unsafe_allow_html=True)
                        else:
                            st.write(QUESTIONS[q_key])
                    with col2:
                        st.session_state.answers[q_key] = st.number_input(
                            "",
                            0, 100,
                            value=int(st.session_state.answers[q_key]) if st.session_state.answers[q_key] else 0,
                            key=q_key
                        )
                
                elif i == 23:  # Duration question
                    col1, col2 = st.columns([10, 2])
                    with col1:
                        if pre_answered:
                            st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;">{QUESTIONS[q_key]}</div>', unsafe_allow_html=True)
                        else:
                            st.write(QUESTIONS[q_key])
                    with col2:
                        st.session_state.answers[q_key] = st.number_input(
                            "",
                            0, 180,
                            value=int(st.session_state.answers[q_key]) if st.session_state.answers[q_key] else 0,
                            key=q_key
                        )
                
                elif i in [24, 26, 27, 28]:  # Frequency questions
                    frequency_buttons(
                        q_key,
                        QUESTIONS[q_key],
                        ['every class', 'every week', 'once in a while', 'rarely'],
                        pre_answered
                    )
                
                elif i == 44:  # Often/sometimes/rarely question
                    frequency_buttons(
                        q_key,
                        QUESTIONS[q_key],
                        ['often', 'sometimes', 'rarely'],
                        pre_answered
                    )
                
                else:  # Yes/No questions
                    yes_no_buttons(q_key, QUESTIONS[q_key], pre_answered)
            
            st.markdown("---")

        if st.button("Submit"):
            if save_to_google_sheets(st.session_state.answers):
                missing_info = []
                for q in range(5, 20):
                    if f'Q{q}' not in st.session_state.uploaded_files_content:
                        missing_info.append(QUESTIONS[f'Q{q}'])
                
                feedback_prompt = f"""
                Based on the following information that couldn't be found in the syllabus: {missing_info},
                provide a brief, friendly suggestion about what additional information could be included in 
                future syllabi. Keep the response under 3 sentences.
                """
                
                feedback_response = amplify_chat(feedback_prompt)
                
                st.success("Thank you for completing the inventory!")
                if feedback_response and 'message' in feedback_response:
                    st.info(feedback_response['message'])
                
                st.session_state.current_step = 'welcome'
                st.session_state.answers = {}
                st.session_state.uploaded_files_content = ""
                st.rerun()

if __name__ == "__main__":
    main()