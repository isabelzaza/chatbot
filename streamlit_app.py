import requests
import json
import streamlit as st
import PyPDF2
import docx
import io

# Define the inventory questions
INVENTORY_QUESTIONS = {
    "Q1": {"question": "Instructor Name", "format": "text"},
    "Q2": {"question": "Course Number", "format": "text"},
    "Q3": {"question": "Semester and Year", "format": "text"},
    "Q4": {"question": "Number of Students", "format": "number"},
    "Q5": {"question": "Do you give students a list of the topics that will be covered in the course?", "format": "y/n"},
    "Q6": {"question": "Do you provide a list of general skills or abilities students should develop (like critical thinking)?", "format": "y/n"},
    "Q7": {"question": "Do you list specific skills or abilities students should learn from specific topics (e.g., from a given activity or lecture)?", "format": "y/n"},
    "Q8": {"question": "Do you articulate a policy regarding permissible and impermissible use of AI tools/LLMs for this class, beyond saying all use of AI tools in assignments is banned?", "format": "y/n"},
    "Q9": {"question": "Do you use a platform for class discussions online?", "format": "y/n"},
    "Q10": {"question": "Do you use a course website like Brightspace to share materials?", "format": "y/n"},
    "Q11": {"question": "Do you provide solutions to homework assignments?", "format": "y/n"},
    "Q12": {"question": "Do you share examples of how to solve problems (e.g., step-by-step guides)?", "format": "y/n"},
    "Q13": {"question": "Do you give practice tests or past exam papers?", "format": "y/n"},
    "Q14": {"question": "Do you post videos, animations, or simulations to explain course content?", "format": "y/n"},
    "Q15": {"question": "Do you share your lecture slides, notes or recording of lectures with students (either before or after class)?", "format": "y/n"},
    "Q16": {"question": "Do you provide other materials, like reading or study aids?", "format": "y/n"},
    "Q17": {"question": "Do you give students access to articles or research related to the course?", "format": "y/n"},
    "Q18": {"question": "Do you share examples of excellent student papers or projects?", "format": "y/n"},
    "Q19": {"question": "Do you provide grading guides/ rubrics to explain how assignments will be marked?", "format": "y/n"},
    "Q20": {"question": "Do you regularly use a strategy to elicit student questions in class -beyond saying are there any questions and moving on?", "format": "y/n"},
    "Q21": {"question": "In a typical class, what is the proportion of time for which students work in small groups?", "format": "percentage (0 to 100)"},
    "Q22": {"question": "In a typical class, what is the proportion of time for which you lecture?", "format": "percentage (0 to 100)"},
    "Q23": {"question": "What is the longest duration you lecture before breaking into an entirely different activity (not just stopping to ask a question or invite questions)?", "format": "number (minutes)"},
    "Q24": {"question": "How often do you use demonstrations, simulations, or videos?", "format": "choice: every class/every week/once in a while/rarely"},
    "Q25": {"question": "If you show a video, do you provide students with detailed instructions of what to look for in the video, and follow-up with a discussion?", "format": "y/n"},
    "Q26": {"question": "How often do you talk about why the material might be useful or interesting from a student's point of view?", "format": "choice: every class/every week/once in a while/rarely"},
    "Q27": {"question": "Do you use a response system (e.g., Top hat) for ungraded activities?", "format": "choice: every class/every week/once in a while/rarely"},
    "Q28": {"question": "Do you use a response system (e.g., Top hat) for graded activities?", "format": "choice: every class/every week/once in a while/rarely"},
    "Q29": {"question": "Do you give homework or practice problems that do not count towards grade?", "format": "y/n"},
    "Q30": {"question": "Do you give homework or problems that count towards grade?", "format": "y/n"},
    "Q31": {"question": "Do you assign a project or paper where students have some choice about the topic?", "format": "y/n"},
    "Q32": {"question": "Do you encourage students to work together on individual assignments?", "format": "y/n"},
    "Q33": {"question": "Do you give group assignments?", "format": "y/n"},
    "Q34": {"question": "Do you ask students for anonymous feedback outside of end of term course reviews", "format": "y/n"},
    "Q35": {"question": "Do you allow students to revise their work based on feedback?", "format": "y/n"},
    "Q36": {"question": "Do students have access to their graded exams and other assignments?", "format": "y/n"},
    "Q37": {"question": "Do you share answer keys for graded exams and other assignments?", "format": "y/n"},
    "Q38": {"question": "Do you require students to include a statement regarding their use of AI tools/LLMs on submitted assignments, or submit some kind of record to delineate which parts of the assignment represent their own intellectual contributions versus those of generative AI?", "format": "y/n"},
    "Q39": {"question": "Do you encourage students to meet with you to discuss their progress?", "format": "y/n"},
    "Q40": {"question": "Do you give a test at the beginning of the course to see what students already know?", "format": "y/n"},
    "Q41": {"question": "Do you use a pre-and-post test to measure how much students learn in the course?", "format": "y/n"},
    "Q42": {"question": "Do you ask students about their interest or feelings about the subject before and after the course?", "format": "y/n"},
    "Q43": {"question": "Do you give students some control over their learning, like choosing topics or how they will be graded?", "format": "y/n"},
    "Q44": {"question": "Do you try new teaching methods or materials and measure how well they work?", "format": "choice: often/sometimes/rarely"},
    "Q45": {"question": "Do you have graduate TAs or undergraduate LAs for this course?", "format": "y/n"},
    "Q46": {"question": "Do you provide TAs/LAs with some training on teaching methods?", "format": "y/n"},
    "Q47": {"question": "Do you meet with TAs/LAs regularly to talk about teaching and how students are doing?", "format": "y/n"},
    "Q48": {"question": "Do you use teaching materials from other instructors?", "format": "y/n"},
    "Q49": {"question": "Do you use some of the same teaching materials as other instructors of the same course in your department?", "format": "y/n"},
    "Q50": {"question": "Do you talk with colleagues about how to teach this course?", "format": "y/n"},
    "Q51": {"question": "Relevant to this course, did you read articles or attend workshops to improve your teaching?", "format": "y/n"},
    "Q52": {"question": "Have you observed another instructor's class to get ideas?", "format": "y/n"}
}

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def process_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
    
    try:
        file_bytes = uploaded_file.getvalue()
        
        if uploaded_file.type == "application/pdf":
            text = read_pdf(io.BytesIO(file_bytes))
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(io.BytesIO(file_bytes))
        else:
            st.error("Unsupported file type. Please upload a PDF or Word document.")
            return None
            
        return text
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def make_llm_request(file_content):
    url = "https://prod-api.vanderbilt.ai/chat"
    
    try:
        API_KEY = st.secrets["AMPLIFY_API_KEY"]
    except KeyError:
        st.error("API key not found in secrets. Please configure your secrets.toml file.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Create a formatted string of all questions
    questions_text = "\n".join([f"{q}: {text}" for q, text in INVENTORY_QUESTIONS.items()])

    prompt = f"""
    Based on the provided document, help answer as many questions as possible from the Vanderbilt Psychology Teaching Inventory. 
    Here are all the questions:

    {questions_text}

    For each question you can answer based on the document, provide:
    1. The question number (Q1-Q52)
    2. The question text
    3. The answer you found, with a brief explanation of where in the document you found this information
    
    Only include questions where you found clear evidence in the document to support the answer.
    Format your response as:
    Q[number]: [Question text]
    Answer: [Your answer]
    Evidence: [Where you found this in the document]
    
    Document content:
    {file_content}
    """

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    payload = {
        "data": {
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_tokens": 4096,
            "dataSources": [],
            "messages": messages,
            "options": {
                "ragOnly": False,
                "skipRag": True,
                "model": {"id": "gpt-4o"},
                "prompt": prompt,
            },
        }
    }

    try:
        with st.spinner('Analyzing document and matching to inventory questions...'):
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("data", "")
            else:
                st.error(f"Request failed with status code {response.status_code}")
                st.error(response.text)
                return None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def main():
    st.title("Vanderbilt Psychology Teaching Inventory Helper")
    
    st.write("""
    The Full inventory has several questions but I want to help you answer them as fast as possible. 
    If you have a syllabus for the course, or any other document relevant to your teaching practices 
    in this course, please upload it (in pdf or .docx format).
    """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your syllabus or teaching document", 
                                   type=["pdf", "docx"])
    
    # Process the file if uploaded
    if uploaded_file:
        with st.spinner('Processing document...'):
            file_content = process_uploaded_file(uploaded_file)
            if file_content:
                st.success("Document processed successfully!")
                if st.checkbox("Show document content"):
                    st.text_area("Document content:", file_content, height=200)
                
                # Automatically analyze the document
                response = make_llm_request(file_content)
                
                # Display the response
                if response:
                    st.subheader("Analysis Results:")
                    st.write(response)
                    st.info("Please review these auto-generated answers and adjust them if needed. The system only provides answers when it finds clear evidence in the document.")

if __name__ == "__main__":
    main()