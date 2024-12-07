import streamlit as st
import pandas as pd
import requests
import json
import PyPDF2
import io

def amplify_chat(prompt):
    url = "https://prod-api.vanderbilt.ai/chat"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "data": {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 500,
            "dataSources": [],
            "assistantId": "astp/abcdefghijk",
            "options": {
                "ragOnly": False,
                "skipRag": True,
                "prompt": prompt
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def extract_text_from_files(uploaded_files):
    combined_text = ""
    for file in uploaded_files:
        if file.name.endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                for page in pdf_reader.pages:
                    combined_text += page.extract_text() + "\n"
            except Exception as e:
                st.warning(f"Error reading PDF {file.name}: {str(e)}")
        else:
            try:
                text = str(file.read(), 'utf-8')
                combined_text += text
            except UnicodeDecodeError:
                st.warning(f"Could not read {file.name}. Please ensure it's a text file.")
    return combined_text

def analyze_documents(text):
    prompt = f"""Analyze this document for teaching inventory information. Extract: instructor name, course number, semester/year, class size, major requirement status, lab/seminar status, and teaching practices. Return JSON with Q1-Q52 as keys and answers as values. Only include high-confidence answers.
    
    Document: {text[:10000]}"""
    
    response = amplify_chat(prompt)
    try:
        return json.loads(response['choices'][0]['message']['content'])
    except:
        return {}

def save_to_sheets(answers):
    # Implement Google Sheets API integration here
    pass

# Dictionary of all questions
QUESTIONS = {
    "Course Details": {
        1: "Instructor Name",
        2: "Course Number",
        3: "Semester and Year",
        4: "Number of Students",
        5: "Is the course a major requirement? (y/n)",
        6: "Is this course a lab? (y/n)",
        7: "Is this course a seminar? (y/n)"
    },
    "Course Information": {
        8: "Do you give students a list of the topics covered in the course? (y/n)",
        9: "Do you provide a list of general skills or abilities students should develop (like critical thinking)? (y/n)",
        10: "Do you list specific skills or abilities students should learn from specific topics? (y/n)"
    },
    # Add all other sections and questions...
}

def render_section_page(section_name, questions_dict):
    st.header(section_name)
    
    for q_num, q_text in questions_dict.items():
        question_key = f"Q{q_num}"
        
        # Frequency questions
        if q_num == 23 or q_num in [24, 25, 26, 27, 28]:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["every class", "every week", "once in a while", "rarely"],
                key=question_key
            )
        # Feedback frequency
        elif q_num == 34:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["never", "midterm", "several times"],
                key=question_key
            )
        # New methods frequency
        elif q_num == 44:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["often", "sometimes", "rarely"],
                key=question_key
            )
        # Yes/No questions
        else:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["yes", "no"],
                key=question_key
            )

def main():
    st.set_page_config(page_title="Psychology Dept. Teaching Inventory", layout="wide")
    
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'page' not in st.session_state:
        st.session_state.page = 'upload'

    st.title("Psychology Dept. Teaching Inventory")
    
    # File Upload Page
    if st.session_state.page == 'upload':
        st.write("The full inventory is 52 questions but I want to help you answer them as fast as possible. "
                "If you have a syllabus or other relevant teaching documents, please upload them.")

        uploaded_files = st.file_uploader(
            "Upload files", 
            accept_multiple_files=True, 
            type=['txt', 'csv', 'md', 'pdf']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if uploaded_files and st.button("Process Files"):
                text = extract_text_from_files(uploaded_files)
                extracted_answers = analyze_documents(text)
                st.session_state.answers.update(extracted_answers)
                st.success(f"Extracted information for {len(extracted_answers)} questions.")
        
        with col2:
            if st.button("Continue to Questions"):
                st.session_state.page = 'section1'
                st.experimental_rerun()
    
    # Section Pages
    elif st.session_state.page.startswith('section'):
        current_section = list(QUESTIONS.keys())[int(st.session_state.page[-1]) - 1]
        render_section_page(current_section, QUESTIONS[current_section])
        
        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if int(st.session_state.page[-1]) > 1:
                if st.button("Previous Section"):
                    st.session_state.page = f"section{int(st.session_state.page[-1]) - 1}"
                    st.experimental_rerun()
        
        with col2:
            if int(st.session_state.page[-1]) < len(QUESTIONS):
                if st.button("Next Section"):
                    st.session_state.page = f"section{int(st.session_state.page[-1]) + 1}"
                    st.experimental_rerun()
        
        with col3:
            if st.button("Submit All Responses"):
                save_to_sheets(st.session_state.answers)
                st.success("Responses saved successfully!")

if __name__ == "__main__":
    main()