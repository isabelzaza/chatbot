import streamlit as st
import pandas as pd
import json
import PyPDF2
import io
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")

def process_with_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant analyzing course documents. Extract information and map it to specific question numbers, providing answers in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
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
    
    response = process_with_openai(prompt)
    if response and hasattr(response, 'choices') and len(response.choices) > 0:
        try:
            content = response.choices[0].message.content
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

# Dictionary of questions by section
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
        
        if uploaded_files:
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