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
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Amplify API: {str(e)}")
        return None

def extract_text_from_files(uploaded_files):
    combined_text = ""
    for file in uploaded_files:
        if file.name.endswith('.pdf'):
            try:
                file.seek(0)
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
                for page in pdf_reader.pages:
                    combined_text += page.extract_text() + "\n"
            except Exception as e:
                st.warning(f"Error reading PDF {file.name}: {str(e)}")
        else:
            try:
                file.seek(0)
                text = str(file.getvalue(), 'utf-8')
                combined_text += text
            except UnicodeDecodeError:
                st.warning(f"Could not read {file.name}. Please ensure it's a text file.")
    return combined_text

def analyze_documents(text):
    prompt = f"""Analyze the following document and extract information about a course. For each piece of information you find, map it to the corresponding question number (Q1-Q52).

Key areas to look for:
- Course Details (Q1-Q7): instructor name, course number, semester, students, requirements
- Course Information (Q8-Q10): topics, skills, learning objectives
- Supporting Materials (Q11-Q21): online platforms, materials, resources
- In-Class Features (Q22-Q28): teaching methods, activities
- Assignments (Q29-Q33): homework, projects, group work
- Feedback and Testing (Q34-Q39): assessment methods
- Other Practices (Q40-Q44): teaching approaches
- TA Information (Q45-47): teaching assistants
- Teaching Collaboration (Q48-52): instructor preparation and collaboration

Return your answers in JSON format where the keys are question numbers (Q1, Q2, etc.) and values are the answers. Only include answers you are confident about based on the document.

Document text: {text[:8000]}"""
    
    response = amplify_chat(prompt)
    if response and 'choices' in response:
        try:
            content = response['choices'][0]['message']['content']
            extracted_answers = json.loads(content)
            return extracted_answers
        except json.JSONDecodeError as e:
            st.error(f"Error parsing AI response: {str(e)}")
            return {}
        except Exception as e:
            st.error(f"Unexpected error processing AI response: {str(e)}")
            return {}
    return {}

def save_to_sheets(answers):
    # Implement Google Sheets API integration here
    st.write("Debug - Answers to save:", answers)
    pass

# [QUESTIONS dictionary stays the same]

def render_section_page(section_name, questions_dict):
    st.header(section_name)
    
    for q_num, q_text in questions_dict.items():
        question_key = f"Q{q_num}"
        current_value = st.session_state.answers.get(question_key, None)
        
        if q_num == 23 or q_num in [24, 25, 26, 27, 28]:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["every class", "every week", "once in a while", "rarely"],
                key=question_key,
                index=["every class", "every week", "once in a while", "rarely"].index(current_value) if current_value else 0
            )
        elif q_num == 34:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["never", "midterm", "several times"],
                key=question_key,
                index=["never", "midterm", "several times"].index(current_value) if current_value else 0
            )
        elif q_num == 44:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["often", "sometimes", "rarely"],
                key=question_key,
                index=["often", "sometimes", "rarely"].index(current_value) if current_value else 0
            )
        else:
            st.session_state.answers[question_key] = st.selectbox(
                f"Question {q_num}: {q_text}",
                ["yes", "no"],
                key=question_key,
                index=["yes", "no"].index(current_value) if current_value else 0
            )

def main():
    st.set_page_config(page_title="Psychology Dept. Teaching Inventory", layout="wide")
    
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'page' not in st.session_state:
        st.session_state.page = 'upload'
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = set()

    st.title("Psychology Dept. Teaching Inventory")
    
    if st.session_state.page == 'upload':
        st.write("The full inventory is 52 questions but I want to help you answer them as fast as possible. "
                "If you have a syllabus or other relevant teaching documents, please upload them.")

        uploaded_files = st.file_uploader(
            "Upload files", 
            accept_multiple_files=True, 
            type=['txt', 'csv', 'md', 'pdf']
        )
        
        # Process files automatically when uploaded
        if uploaded_files:
            # Process only new files
            new_files = []
            for file in uploaded_files:
                if file.name not in st.session_state.processed_files:
                    new_files.append(file)
                    st.session_state.processed_files.add(file.name)
            
            if new_files:
                with st.spinner('Processing uploaded files...'):
                    text = extract_text_from_files(new_files)
                    extracted_answers = analyze_documents(text)
                    st.session_state.answers.update(extracted_answers)
                    st.success(f"Processed {len(new_files)} new file(s) and found information for {len(extracted_answers)} questions.")

        if st.button("Continue to Questions"):
            st.session_state.page = 'section1'
    
    elif st.session_state.page.startswith('section'):
        current_section = list(QUESTIONS.keys())[int(st.session_state.page[-1]) - 1]
        render_section_page(current_section, QUESTIONS[current_section])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if int(st.session_state.page[-1]) > 1:
                if st.button("Previous Section"):
                    st.session_state.page = f"section{int(st.session_state.page[-1]) - 1}"
        
        with col2:
            if int(st.session_state.page[-1]) < len(QUESTIONS):
                if st.button("Next Section"):
                    st.session_state.page = f"section{int(st.session_state.page[-1]) + 1}"
        
        with col3:
            if st.button("Submit All Responses"):
                save_to_sheets(st.session_state.answers)
                st.success("Responses saved successfully!")

if __name__ == "__main__":
    main()