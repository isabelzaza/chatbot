5


I want to build a small application using streamlit through github codespaces. The app is called “Psychology Dept. Teaching Inventory” that I can send to my users via a link through email. It will no
pasted
IG

I'll help you create this Streamlit application. Let's break it down into components and build it step by step. First, I'll create the main application structure with file upload and security handling for the API key.


Psychology Department Teaching Inventory Application
Click to open code
This application implements all the requested functionality. To run it, you'll need to:

Create a .env file with the following variables:

Copy
AMPLIFY_API_KEY=your_key_here
AMPLIFY_ASSISTANT_ID=your_assistant_id_here
GOOGLE_SHEETS_CREDENTIALS=your_service_account_json_here
Install the required packages:
bash

Copy
pip install streamlit pandas google-auth gspread requests PyPDF2 python-dotenv
Run the application:
bash

Copy
streamlit run app.py
The application features:

File upload for syllabus and other documents
Automatic extraction of answers using Amplify API
Section-by-section question interface
Appropriate input types for different question formats
Google Sheets integration for saving responses
Feedback generation about missing syllabus information
Would you like me to:

Add any additional features or modifications?
Explain any part of the code in more detail?
Help with setting up the Google Sheets credentials?
Copy
Retry



image.png
IG
what do I put here:


I notice this appears to be a screenshot showing an OpenAI API key. I should point out that this key appears to be exposed and should be considered compromised. I recommend:

Immediately rotating/regenerating this API key in your OpenAI account
Never sharing API keys in screenshots or public repositories
Using environment variables or secret management systems to handle sensitive credentials
For your Streamlit app, you'll want to:

Create a .streamlit/secrets.toml file in your project directory
Add your keys there in TOML format:
toml

Copy
AMPLIFY_API_KEY = "your-amplify-key"
AMPLIFY_ASSISTANT_ID = "your-assistant-id"
GOOGLE_SHEETS_CREDENTIALS = """your-service-account-json"""
Then in your code, you can access these secrets using:

python

Copy
st.secrets["AMPLIFY_API_KEY"]
st.secrets["AMPLIFY_ASSISTANT_ID"]
st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
This is more secure than using environment variables since Streamlit handles the encryption and secure storage of these secrets. Just make sure to add .streamlit/secrets.toml to your .gitignore file to prevent it from being committed to version control.

Would you like me to modify the code to use Streamlit's secrets management instead of environment variables?

Copy
Retry



IG
what is AMPLIFY_ASSISTANT_ID?


The AMPLIFY_ASSISTANT_ID is a unique identifier for your Vanderbilt Amplify deployment. Looking at your example code, it's the value you would put in the "assistant_id" field, which in your example was shown as "astp/abcdefghijk".

You should be able to get your specific AMPLIFY_ASSISTANT_ID from your Vanderbilt Amplify account settings or documentation. If you don't have this value, you should:

Check your Vanderbilt Amplify dashboard or settings
Contact Vanderbilt Amplify support
Check any documentation provided when you got your Amplify API access
The assistant_id helps route your requests to the correct model and configuration within the Amplify system. Would you like me to help adjust the code to work with a specific assistant_id once you have it?

Copy
Retry


IG
please modify the code to use Streamlit's secrets management instead of environment variables


I'll modify the code to use Streamlit's secrets management system.


Psychology Department Teaching Inventory Application
Click to open code
To use this updated version, you'll need to:

Create a .streamlit/secrets.toml file in your project directory with:
toml

Copy
AMPLIFY_API_KEY = "your-amplify-key"
AMPLIFY_ASSISTANT_ID = "your-assistant-id"
GOOGLE_SHEETS_CREDENTIALS = """your-service-account-json"""
Install the required packages:
bash

Copy
pip install streamlit pandas google-auth gspread requests PyPDF2
Run the application:
bash

Copy
streamlit run app.py
Key changes made:

Removed the load_dotenv() and related environment variable handling
Replaced all os.getenv() calls with st.secrets[] access
Removed the dotenv package requirement
The functionality remains the same, but the secrets management is now more secure using Streamlit's built-in system. Would you like me to explain any part of the secrets management in more detail?

Copy
Retry



IG
ok, so the app was created but there are 2 problems. 1 - it doesn't show the questions, and 2- it didn't get any information from the syllabus I uploaded


Let's debug both issues:

For the questions not showing: We need to display the actual question text, not just "Q1", "Q2" etc. Let's create a dictionary with all the questions.
For the syllabus extraction: We should modify the prompt to make it more specific and add some error checking to see
Copy
Retry


image.png
IG

I see the issue - we're not displaying the actual question text, just the question numbers. Let's modify the code to include the full questions. Here's the fix:


Psychology Department Teaching Inventory Application
Click to open code
Key changes made:

Added a QUESTIONS dictionary with all the full question text
Modified the questions display to use the full text instead of just Q1, Q2, etc.
Improved the syllabus analysis by:
Adding more specific prompting
Adding debug information to see what's being extracted
Making the analysis more conservative (defaulting to 'n' when uncertain)
The code now should show the full questions and provide better syllabus analysis. Would you like me to make any adjustments to how the questions are displayed or how the syllabus analysis works?

Copy
Retry


image.png
IG
right now, I can't tell which questions have been answered through uploaded information or still needs my answers (I only see pull down menus) Can we make the questions already answered in a shade of green?- also, is it possible to use button responses arranged horizontally instead of pull down menus?


Yes, let's modify the display to make it clearer which questions were automatically answered and use horizontal buttons instead of dropdowns.


Psychology Department Teaching Inventory Application
Click to open code
Key changes made:

Added green background highlighting for pre-answered questions
Replaced dropdowns with horizontal buttons for yes/no questions
Added horizontal buttons for frequency questions
Improved layout with columns to keep buttons aligned
Added visual feedback for current selections
Maintained the auto-filled answers from document analysis
The questions that were automatically answered from the uploaded documents will now appear with a green background, and all yes/no questions use horizontal buttons instead of dropdowns. Would you like me to:

Adjust the styling of the buttons or highlighting?
Modify the layout of the buttons?
Add any additional visual indicators for the pre-answered questions?
Copy
Retry


IG
I got File "/mount/src/chatbot/streamlit_app.py", line 49 elif st.session_state.current_step == 'questions': ^ SyntaxError: invalid syntax


The error is occurring because we're missing some code structure. Let me provide the complete file, properly organized:


Psychology Department Teaching Inventory Application
Click to open code
The main changes are:

Properly structured all the code inside functions
Added a main() function to handle the app flow
Put all the session state initialization at the top
Fixed indentation and organization
The app should now run without syntax errors. Let me know if you'd like me to make any adjustments to the UI or functionality!

Copy
Retry


IG
KeyError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:


Copy
File "/mount/src/chatbot/streamlit_app.py", line 284, in <module>
    main()
File "/mount/src/chatbot/streamlit_app.py", line 255, in main yes_no_buttons(q_key, QUESTIONS[q_key], pre_answered) ~~~~~~~~~^^^^^^^


The error is occurring because we don't have all the questions defined in our QUESTIONS dictionary. Let me fix that by including all questions:


Psychology Department Teaching Inventory Application - Questions Dictionary
Click to open code
Replace the QUESTIONS dictionary at the top of your file with this complete version. All other code can remain the same. This should resolve the KeyError you're seeing.

Would you like me to:

Add any additional modifications to the questions or their formatting?
Make any adjustments to how the questions are displayed in the interface?
Add any other features to the application?
Copy
Retry


image.png
IG
I get this error. also, some questions are not yes/no and in that case, it is more appropriate to let the person type in the name or to have a slider (for percentage). I also still have the problem that the app does not extract information from my uploaded file


Let's fix these issues one by one:

First, let's fix the error with the value conversion and modify the input types for different questions
Then we'll improve the document analysis part

Psychology Department Teaching Inventory Application
Click to open code
Key changes made:

Fixed input types:
Added text input fields for the first 4 questions (instructor, course number, etc.)
Fixed the percentage sliders to properly handle initial values
Added proper error handling for value conversion
Improved document analysis:
Split analysis into two passes: basic information and yes/no questions
Added more detailed feedback during analysis
Improved prompting for better information extraction
Added debug information to see what's being extracted
Added feedback during file processing:
Shows success messages for each processed file
Shows what information was extracted
Would you like me to:

Modify how any of the input types work?
Adjust the document analysis further?
Add more detailed feedback about what information was found in the uploaded documents?
Copy
Retry


IG
give me the entire code please


I'll provide the complete code in a single piece.


Complete Psychology Department Teaching Inventory Application
Click to open code
Copy
Retry



IG
is it only trying to use LLM to extract the first section answers?


No, looking at the analyze_syllabus() function, it's trying to extract two types of information:

Basic information (First pass):
python

Copy
# First pass: Extract basic information (Q1-Q4)
basic_info_prompt = """
From the provided document, extract the following information. 
Respond in JSON format:
{
    "instructor": "name or empty if not found",
    "course_number": "number or empty if not found",
    "semester": "semester and year or empty if not found",
    "students": "number or empty if not found"
}
"""
Yes/No questions (Second pass):
python

Copy
yn_questions = {
    'Q5': 'Is there a list of topics or course schedule?',
    'Q6': 'Are general learning objectives or skills mentioned?',
    'Q7': 'Are specific learning objectives for topics mentioned?',
    'Q8': 'Is there an AI/LLM policy?',
    'Q9': 'Is an online discussion platform mentioned?',
    'Q10': 'Is Brightspace or another course website mentioned?',
    'Q11': 'Are homework solutions mentioned?',
    'Q12': 'Are problem-solving examples mentioned?',
    'Q13': 'Are practice tests or past exams mentioned?',
    'Q14': 'Are videos, animations, or simulations mentioned?',
    'Q15': 'Are lecture slides, notes, or recordings mentioned?',
    'Q16': 'Are reading materials or study aids mentioned?',
    'Q17': 'Are course-related articles or research mentioned?',
    'Q18': 'Are example student works mentioned?',
    'Q19': 'Are grading rubrics mentioned?'
}
However, you're right - it's only trying to automatically extract answers for Q1-Q19. We could expand this to try to extract information for the other sections as well. Would you like me to modify the code to attempt extraction of answers for all questions?

Copy
Retry



IG
yes, I want it to try to extract as much from syllabus as possible (give me the full code that follows the list of questions)


I'll continue with the code that includes expanded syllabus analysis for all sections.


Psychology Teaching Inventory Application - Continued
Click to open code
For the syllabus analysis part, replace the previous analyze_syllabus() function with this more comprehensive version:


Comprehensive Syllabus Analysis Function
Click to open code
The improved syllabus analysis now:

Extracts basic course information (Q1-Q4)
Tries to find numerical/frequency information (Q21-24, Q26)
Attempts to extract yes/no answers for all applicable questions
Shows what information it finds in real-time
Takes a conservative approach (only marks 'yes' when there's clear evidence)
Would you like me to modify the analysis approach or add any additional features?

Copy
Retry


IG
ok, so I am not sure what "Shows what information it finds in real-time" but my goal is to make this app as time effective for hte user as possible, so I don't want the user to waste time on answers that were found in teh syllabus (I want them to see the answer that was found, do nothing if it is ok, and be able to modify it easily). Give me the full code please


You're right - we should make it very clear to users which answers were found in the syllabus and make it easy for them to review and modify if needed. I'll provide the complete code with this improved interface.

The code is quite long, so I'll need to split it into a few messages. Here's part 1 with the initial setup and helper functions:


Psychology Teaching Inventory Application - Part 1
Click to open code
Copy
Retry


Claude can make mistakes. Please double-check responses.



No file chosen

3.5 Sonnet

Choose style
Tip:
Long chats cause you to reach your usage limits faster.
Start a new chat 

Psychology Teaching Inventory Application - Part 1

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
    "Q5": "Do you give students a list of the topics that will be covered in the course?",
    "Q6": "Do you provide a list of general skills or abilities students should develop (like critical thinking)?",
    "Q7": "Do you list specific skills or abilities students should learn from specific topics (e.g., from a given activity or lecture)?",
    "Q8": "Do you articulate a policy regarding permissible and impermissible use of AI tools/LLMs for this class, beyond saying all use of AI tools in assignments is banned?",
    "Q9": "Do you use a platform for class discussions online?",
    "Q10": "Do you use a course website like Brightspace to share materials?",
    "Q11": "Do you provide solutions to homework assignments?",
    "Q12": "Do you share examples of how to solve problems (e.g., step-by-step guides)?",
    "Q13": "Do you give practice tests or past exam papers?",
    "Q14": "Do you post videos, animations, or simulations to explain course content?",
    "Q15": "Do you share your lecture slides, notes or recording of lectures with students (either before or after class)?",
    "Q16": "Do you provide other materials, like reading or study aids?",
    "Q17": "Do you give students access to articles or research related to the course?",
    "Q18": "Do you share examples of excellent student papers or projects?",
    "Q19": "Do you provide grading guides/ rubrics to explain how assignments will be marked?",
    "Q20": "Do you regularly use a strategy to elicit student questions in class -beyond saying are there any questions and moving on?",
    "Q21": "In a typical class, what is the proportion of time for which students work in small groups? (percentage, for 0 to 100)",
    "Q22": "In a typical class, what is the proportion of time for which you lecture? (percentage, 0 to 100)",
    "Q23": "What is the longest duration you lecture before breaking into an entirely different activity (not just stopping to ask a question or invite questions)? (number of min)",
    "Q24": "How often do you use demonstrations, simulations, or videos?",
    "Q25": "If you show a video, do you provide students with detailed instructions of what to look for in the video, and follow-up with a discussion?",
    "Q26": "How often do you talk about why the material might be useful or interesting from a student's point of view?",
    "Q27": "Do you use a response system (e.g., Top hat) for ungraded activities?",
    "Q28": "Do you use a response system (e.g., Top hat) for graded activities?",
    "Q29": "Do you give homework or practice problems that do not count towards grade?",
    "Q30": "Do you give homework or problems that count towards grade?",
    "Q31": "Do you assign a project or paper where students have some choice about the topic?",
    "Q32": "Do you encourage students to work together on individual assignments?",
    "Q33": "Do you give group assignments?",
    "Q34": "Do you ask students for anonymous feedback outside of end of term course reviews?",
    "Q35": "Do you allow students to revise their work based on feedback?",
    "Q36": "Do students have access to their graded exams and other assignments?",
    "Q37": "Do you share answer keys for graded exams and other assignments?",
    "Q38": "Do you require students to include a statement regarding their use of AI tools/LLMs on submitted assignments, or submit some kind of record to delineate which parts of the assignment represent their own intellectual contributions versus those of generative AI?",
    "Q39": "Do you encourage students to meet with you to discuss their progress?",
    "Q40": "Do you give a test at the beginning of the course to see what students already know?",
    "Q41": "Do you use a pre-and-post test to measure how much students learn in the course?",
    "Q42": "Do you ask students about their interest or feelings about the subject before and after the course?",
    "Q43": "Do you give students some control over their learning, like choosing topics or how they will be graded?",
    "Q44": "Do you try new teaching methods or materials and measure how well they work?",
    "Q45": "Do you have graduate TAs or undergraduate LAs for this course?",
    "Q46": "Do you provide TAs/LAs with some training on teaching methods?",
    "Q47": "Do you meet with TAs/LAs regularly to talk about teaching and how students are doing?",
    "Q48": "Do you use teaching materials from other instructors?",
    "Q49": "Do you use some of the same teaching materials as other instructors of the same course in your department?",
    "Q50": "Do you talk with colleagues about how to teach this course?",
    "Q51": "Relevant to this course, did you read articles or attend workshops to improve your teaching?",
    "Q52": "Have you observed another instructor's class to get ideas?"
}

# Initialize session state variables
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'welcome'
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'uploaded_files_content' not in st.session_state:
    st.session_state.uploaded_files_content = ""
if 'auto_filled' not in st.session_state:
    st.session_state.auto_filled = set()  # Keep track of which answers were automatically filled

def display_question(key, question, pre_answered=False):
    """Display the question with appropriate styling"""
    if pre_answered:
        st.markdown(
            f"""
            <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <span style="color: #155724;">{question}</span>
                <span style="color: #28a745; float: right;">✓ Auto-filled</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.write(question)

def text_input_field(key, question):
    """Create a text input field for free-form answers"""
    pre_answered = key in st.session_state.auto_filled
    
    display_question(key, question, pre_answered)
    
    value = st.session_state.answers.get(key, "")
    new_value = st.text_input(
        "Edit if needed:", 
        value=value,
        key=f"text_{key}"
    )
    
    if new_value != value:
        st.session_state.answers[key] = new_value
        if key in st.session_state.auto_filled:
            st.session_state.auto_filled.remove(key)

def yes_no_buttons(key, question):
    """Create yes/no buttons with auto-fill indication"""
    pre_answered = key in st.session_state.auto_filled
    
    display_question(key, question, pre_answered)
    
    col1, col2 = st.columns(2)
    current_value = st.session_state.answers.get(key, "")
    
    with col1:
        if st.button('Yes', 
                    key=f'{key}_yes',
                    type='primary' if current_value == 'y' else 'secondary'):
            st.session_state.answers[key] = 'y'
            if key in st.session_state.auto_filled:
                st.session_state.auto_filled.remove(key)
            st.rerun()
    
    with col2:
        if st.button('No',
                    key=f'{key}_no',
                    type='primary' if current_value == 'n' else 'secondary'):
            st.session_state.answers[key] = 'n'
            if key in st.session_state.auto_filled:
                st.session_state.auto_filled.remove(key)
            st.rerun()
 def frequency_buttons(key, question, options):
    """Create frequency selection buttons with auto-fill indication"""
    pre_answered = key in st.session_state.auto_filled
    
    display_question(key, question, pre_answered)
    
    cols = st.columns(len(options))
    current_value = st.session_state.answers.get(key, "")
    
    for option, col in zip(options, cols):
        with col:
            if st.button(
                option,
                key=f'{key}_{option}',
                type='primary' if current_value == option else 'secondary'
            ):
                st.session_state.answers[key] = option
                if key in st.session_state.auto_filled:
                    st.session_state.auto_filled.remove(key)
                st.rerun()

def number_input_field(key, question, min_val, max_val, unit=""):
    """Create a number input field with auto-fill indication"""
    pre_answered = key in st.session_state.auto_filled
    
    display_question(key, question, pre_answered)
    
    current_val = st.session_state.answers.get(key, "0")
    try:
        current_val = int(float(current_val))
    except (ValueError, TypeError):
        current_val = 0
    
    new_val = st.number_input(
        f"Edit if needed ({unit}):",
        min_value=min_val,
        max_value=max_val,
        value=current_val,
        key=f"number_{key}"
    )
    
    if new_val != current_val:
        st.session_state.answers[key] = str(new_val)
        if key in st.session_state.auto_filled:
            st.session_state.auto_filled.remove(key)

def amplify_chat(prompt, content=""):
    """Make a call to Amplify API with proper error handling"""
    url = "https://prod-api.vanderbilt.ai/chat"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "data": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 1000,
            "dataSources": [],
            "assistantId": st.secrets["AMPLIFY_ASSISTANT_ID"],
            "options": {
                "ragOnly": False,
                "skipRag": True,
                "prompt": f"""Context: {content}\n\nQuestion: {prompt}
                Please be very conservative in your answers. Only say 'yes' if you find explicit evidence in the document."""
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
    with st.spinner("Analyzing uploaded document to pre-fill answers..."):
        extraction_prompts = {
            # Basic information
            "course_info": {
                "prompt": """Extract the following information from the document. 
                Respond in JSON format:
                {
                    "instructor": "name or empty if not found",
                    "course_number": "number or empty if not found",
                    "semester": "semester and year or empty if not found",
                    "students": "number or empty if not found"
                }""",
                "mapping": {
                    "instructor": "Q1",
                    "course_number": "Q2",
                    "semester": "Q3",
                    "students": "Q4"
                }
            },
            # Numerical information
            "numerical_info": {
                "prompt": """Extract the following information. 
                Respond in JSON format:
                {
                    "group_work_time": "percentage (0-100) or empty if not found",
                    "lecture_time": "percentage (0-100) or empty if not found",
                    "lecture_duration": "maximum duration in minutes or empty if not found"
                }""",
                "mapping": {
                    "group_work_time": "Q21",
                    "lecture_time": "Q22",
                    "lecture_duration": "Q23"
                }
            }
        }

        # Process structured information first
        for info_type, details in extraction_prompts.items():
            response = amplify_chat(details["prompt"], content)
            if response and 'message' in response:
                try:
                    info = json.loads(response['message'])
                    for key, q_num in details["mapping"].items():
                        if info.get(key):
                            st.session_state.answers[q_num] = info[key]
                            st.session_state.auto_filled.add(q_num)
                except json.JSONDecodeError:
                    st.error(f"Error parsing {info_type}")

        # Process all yes/no questions
        for i in range(5, 53):  # Skip first 4 questions which are handled above
            if i not in [21, 22, 23]:  # Skip numerical questions handled above
                q_key = f'Q{i}'
                prompt = f"""Based on the syllabus content, answer with only 'y' or 'n':
                {QUESTIONS[q_key]}
                Only answer 'y' if you find explicit evidence in the document."""
                
                response = amplify_chat(prompt, content)
                if response and 'message' in response:
                    answer = response['message'].strip().lower()
                    if answer in ['y', 'n']:
                        st.session_state.answers[q_key] = answer
                        st.session_state.auto_filled.add(q_key)

        # Show summary of what was found
        num_found = len(st.session_state.auto_filled)
        if num_found > 0:
            st.success(f"Successfully pre-filled {num_found} answers from your document. Please review and modify if needed.")
        else:
            st.warning("Could not automatically extract any answers from the document. Please fill in the questions manually.")
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

def main():
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
                        content = extract_text_from_pdf(file)
                        if content:
                            st.session_state.uploaded_files_content += content
                    else:
                        content = str(file.read(), 'utf-8')
                        st.session_state.uploaded_files_content += content
                
                if st.session_state.uploaded_files_content:
                    analyze_syllabus(st.session_state.uploaded_files_content)
            
            st.session_state.current_step = 'questions'
            st.rerun()

    # Questions screen
    elif st.session_state.current_step == 'questions':
        st.title("Course Information")
        
        # Progress bar
        total_questions = 52
        answered_questions = len([k for k in st.session_state.answers.keys() if st.session_state.answers[k] != ""])
        progress = answered_questions / total_questions
        st.progress(progress)
        st.write(f"Progress: {answered_questions}/{total_questions} questions answered")
        
        for section, q_range in sections.items():
            st.header(section)
            for i in q_range:
                q_key = f'Q{i}'
                
                # Text input for first four questions
                if i <= 4:
                    text_input_field(q_key, QUESTIONS[q_key])
                
                # Percentage sliders
                elif i in [21, 22]:
                    number_input_field(q_key, QUESTIONS[q_key], 0, 100, "percentage")
                
                # Duration input
                elif i == 23:
                    number_input_field(q_key, QUESTIONS[q_key], 0, 180, "minutes")
                
                # Frequency questions
                elif i in [24, 26, 27, 28]:
                    frequency_buttons(
                        q_key,
                        QUESTIONS[q_key],
                        ['every class', 'every week', 'once in a while', 'rarely']
                    )
                
                # Often/sometimes/rarely question
                elif i == 44:
                    frequency_buttons(
                        q_key,
                        QUESTIONS[q_key],
                        ['often', 'sometimes', 'rarely']
                    )
                
                # Yes/No questions for all others
                else:
                    yes_no_buttons(q_key, QUESTIONS[q_key])
            
            st.markdown("---")

        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.button("Submit", type="primary")
        
        if submit_button:
            with st.spinner("Saving your responses..."):
                if save_to_google_sheets(st.session_state.answers):
                    feedback_prompt = """
                    Based on the syllabus content provided, what are the most important items 
                    that could be added to make the syllabus more comprehensive? Focus on items 
                    that weren't found in the current syllabus. Keep the response brief and constructive.
                    """
                    
                    feedback_response = amplify_chat(feedback_prompt, st.session_state.uploaded_files_content)
                    
                    st.success("Thank you for completing the inventory!")
                    if feedback_response and 'message' in feedback_response:
                        st.info(feedback_response['message'])
                    
                    # Reset for next use
                    st.session_state.current_step = 'welcome'
                    st.session_state.answers = {}
                    st.session_state.uploaded_files_content = ""
                    st.session_state.auto_filled = set()
                    st.rerun()

if __name__ == "__main__":
    main()           