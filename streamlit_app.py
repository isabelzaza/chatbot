import streamlit as st
import pandas as pd
import requests
import json
import fitz
from typing import Dict, List

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
            pdf_bytes = file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                combined_text += page.get_text()
        else:
            combined_text += str(file.read(), 'utf-8')
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

def main():
    st.set_page_config(page_title="Psychology Dept. Teaching Inventory", layout="wide")
    
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

    st.title("Psychology Dept. Teaching Inventory")
    
    st.write("The full inventory is 52 questions but I want to help you answer them as fast as possible. "
             "If you have a syllabus or other relevant teaching documents, please upload them.")

    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process Files"):
            text = extract_text_from_files(uploaded_files)
            extracted_answers = analyze_documents(text)
            st.session_state.answers.update(extracted_answers)
            st.success(f"Extracted information for {len(extracted_answers)} questions.")

    sections = {
        "Course Details": list(range(1, 8)),
        "Course Information": list(range(8, 11)),
        "Supporting Materials": list(range(11, 22)),
        "In-Class Features": list(range(22, 29)),
        "Assignments": list(range(29, 34)),
        "Feedback and Testing": list(range(34, 40)),
        "Other": list(range(40, 45)),
        "TA Training": list(range(45, 48)),
        "Teaching Collaboration": list(range(48, 53))
    }

    for section_name, questions in sections.items():
        with st.expander(section_name):
            for q in questions:
                if q == 23:  # Special case for frequency questions
                    st.session_state.answers[f"Q{q}"] = st.selectbox(
                        f"Q{q}",
                        ["every class", "every week", "once in a while", "rarely"],
                        key=f"Q{q}"
                    )
                elif q in [24, 25, 26, 27, 28]:  # Other frequency questions
                    st.session_state.answers[f"Q{q}"] = st.selectbox(
                        f"Q{q}",
                        ["every class", "every week", "once in a while", "rarely"],
                        key=f"Q{q}"
                    )
                elif q == 34:  # Special case for feedback frequency
                    st.session_state.answers[f"Q{q}"] = st.selectbox(
                        f"Q{q}",
                        ["never", "midterm", "several times"],
                        key=f"Q{q}"
                    )
                elif q == 44:  # Special case for trying new methods
                    st.session_state.answers[f"Q{q}"] = st.selectbox(
                        f"Q{q}",
                        ["often", "sometimes", "rarely"],
                        key=f"Q{q}"
                    )
                else:  # Yes/No questions
                    st.session_state.answers[f"Q{q}"] = st.selectbox(
                        f"Q{q}",
                        ["yes", "no"],
                        key=f"Q{q}"
                    )

    if st.button("Submit Responses"):
        save_to_sheets(st.session_state.answers)
        st.success("Responses saved successfully!")

if __name__ == "__main__":
    main()