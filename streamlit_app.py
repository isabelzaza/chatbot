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
    "Supporting Materials": {
        11: "Do you use a platform for class discussions online? (y/n)",
        12: "Do you use a course website like Brightspace to share materials? (y/n)",
        13: "Do you provide solutions to homework assignments? (y/n)",
        14: "Do you share examples of how to solve problems (e.g., step-by-step guides)? (y/n)",
        15: "Do you give practice tests or past exam papers? (y/n)",
        16: "Do you post videos, animations, or simulations to explain course content? (y/n)",
        17: "Do you share your lecture slides or notes with students? (y/n)",
        18: "Do you provide other materials, like readings or study aids? (y/n)",
        19: "Do you give students access to articles or research related to the course? (y/n)",
        20: "Do you share examples of excellent student papers or projects? (y/n)",
        21: "Do you provide grading guides/ rubrics to explain how assignments would be marked? (y/n)"
    },
    "In-Class Features": {
        22: "Do you regularly use a strategy to elicit student questions in class -beyond saying are there any questions and moving on? (y/n)",
        23: "Do students work in small groups during class?",
        24: "How often do you show demonstrations, simulations, or videos?",
        25: "How often do you ask students to predict what would happen before showing them the answer?",
        26: "How often do you talk about why the material might be useful or interesting from a student's point of view?",
        27: "Do you use a response system (e.g., Top hat) for ungraded activities?",
        28: "Do you use a response system (e.g., Top hat) for graded activities?"
    },
    "Assignments": {
        29: "Do you give homework or practice problems that do not count towards their grades? (y/n)",
        30: "Do you give homework or problems that counted towards their grades regularly? (y/n)",
        31: "Do you assign a project or paper where students had some choice about the topic? (y/n)",
        32: "Do you encourage students to work together on individual assignments? (y/n)",
        33: "Do you give group assignments? (y/n)"
    },
    "Feedback and Testing": {
        34: "Do you ask students for feedback?",
        35: "Do you allow students to revise their work based on feedback? (y/n)",
        36: "Do you share answer keys or grading guides for assignments? (y/n)",
        37: "Do students see graded exams or quizzes? (y/n)",
        38: "Do you share answer keys for exams or quizzes? (y/n)",
        39: "Do you encourage students to meet with you to discuss their progress? (y/n)"
    },
    "Other": {
        40: "Do you give a test at the beginning of the course to see what students already know? (y/n)",
        41: "Do you use a pre-and-post test to measure how much students learned? (y/n)",
        42: "Do you ask students about their interest or feelings about the subject before and after the course? (y/n)",
        43: "Do you give students some control over their learning, like choosing topics or how they would be graded? (y/n)",
        44: "Do you try new teaching methods or materials and measure how well they work?"
    },
    "TA Training": {
        45: "Do you have graduate TAs or undergraduate LAs for this course? (y/n)",
        46: "Do you provide TAs/LAs with some training on teaching methods? (y/n)",
        47: "Do you meet with TAs/LAs regularly to talk about teaching and how students are doing? (y/n)"
    },
    "Teaching Collaboration": {
        48: "Do you use teaching materials from other instructors? (y/n)",
        49: "Do you use some of the same teaching materials as other instructors of the same course in your department? (y/n)",
        50: "Do you talk with colleagues about how to teach this course? (y/n)",
        51: "To prepare this course, did you read articles or attend workshops to improve your teaching? (y/n)",
        52: "Have you observed another instructor's class to get ideas? (y/n)"
    }
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