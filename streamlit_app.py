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
            f'''
            <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <span style="color: #155724;">{question}</span>
                <span style="color: #28a745; float: right;">✓ Auto-filled</span>
            </div>
            ''', 
            unsafe_allow_html=True
        )
    else:
        st.write(question)

def text_input_field(key, question):
    """Create a text input field for free-form answers"""
    pre_answered = key in st.session_state.auto_filled
    
    display_question(key, question, pre_answered)
    
    value = st.session_state.answers.get(key, '')
    new_value = st.text_input(
        'Edit if needed:', 
        value=value,
        key=f'text_{key}'
    )
    
    if new_value != value:
        st.session_state.answers[key] = new_value
        if key in st.session_state.auto_filled:
            st.session_state.auto_filled.remove(key)

def yes_no_buttons(key, question):
    """Create yes/no buttons with auto-fill indication"""
    pre_answered = key in st.session_state.auto_filled
    
    display_question(key, question, pre_answered)
    
    # Create a container to hold the buttons close together
    button_container = st.container()
    
    # Use columns with smaller ratios and more columns for spacing
    col1, col2, col3, col4, col5 = button_container.columns([1, 1, 0.2, 1, 1])
    current_value = st.session_state.answers.get(key, '')
    
    with col2:
        if st.button('Yes', 
                    key=f'{key}_yes',
                    type='primary' if current_value == 'y' else 'secondary'):
            st.session_state.answers[key] = 'y'
            if key in st.session_state.auto_filled:
                st.session_state.auto_filled.remove(key)
            st.rerun()
    
    with col4:
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
    
    # Create a container to hold the buttons close together
    button_container = st.container()
    
    # Calculate columns - we want small spaces between buttons
    num_options = len(options)
    # Create 2*num_options-1 columns to add spacing between buttons
    cols = button_container.columns([1 if i % 2 == 0 else 0.2 for i in range(2*num_options-1)])
    current_value = st.session_state.answers.get(key, '')
    
    # Use only the even-numbered columns (odd-numbered are spacers)
    for i, option in enumerate(options):
        with cols[i*2]:  # This skips the spacing columns
            if st.button(
                option,
                key=f'{key}_{option}',
                type='primary' if current_value == option else 'secondary'
            ):
                st.session_state.answers[key] = option
                if key in st.session_state.auto_filled:
                    st.session_state.auto_filled.remove(key)
                st.rerun()

def number_input_field(key, question, min_val, max_val, unit=''):
    """Create a number input field or slider with auto-fill indication"""
    pre_answered = key in st.session_state.auto_filled
    
    display_question(key, question, pre_answered)
    
    current_val = st.session_state.answers.get(key, '0')
    try:
        current_val = int(float(current_val))
    except (ValueError, TypeError):
        current_val = 0
    
    if unit == 'percentage':
        new_val = st.slider(
            f'Edit if needed ({unit}):',
            min_value=min_val,
            max_value=max_val,
            value=current_val,
            key=f'slider_{key}'
        )
    else:
        new_val = st.number_input(
            f'Edit if needed ({unit}):',
            min_value=min_val,
            max_value=max_val,
            value=current_val,
            key=f'number_{key}'
        )
    
    if new_val != current_val:
        st.session_state.answers[key] = str(new_val)
        if key in st.session_state.auto_filled:
            st.session_state.auto_filled.remove(key)
            
def amplify_chat(prompt, content=''):
    """Make a call to Amplify API with proper error handling"""
    url = 'https://prod-api.vanderbilt.ai/chat'
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        'data': {
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000,
            'dataSources': [],
            'assistantId': st.secrets['AMPLIFY_ASSISTANT_ID'],
            'options': {
                'ragOnly': False,
                'skipRag': True,
                'prompt': f'''Context: {content}\n\nQuestion: {prompt}
                Please be very conservative in your answers. Only say 'yes' if you find explicit evidence in the document.'''
            }
        }
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            data=json.dumps(payload),
            auth=(st.secrets['AMPLIFY_API_KEY'], '')
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f'Error calling Amplify API: {str(e)}')
        return None
    
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        text = ''
        for page in pdf_reader:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f'Error reading PDF: {str(e)}')
        return ''

def analyze_syllabus(content):
    """Analyze syllabus content to extract answers"""
    with st.spinner('Analyzing uploaded document to pre-fill answers...'):
        extraction_prompts = {
            # Basic information
            'course_info': {
                'prompt': '''Extract the following information from the document. 
                Respond in JSON format:
                {
                    "instructor": "name or empty if not found",
                    "course_number": "number or empty if not found",
                    "semester": "semester and year or empty if not found",
                    "students": "number or empty if not found"
                }''',
                'mapping': {
                    'instructor': 'Q1',
                    'course_number': 'Q2',
                    'semester': 'Q3',
                    'students': 'Q4'
                }
            },
            # Numerical information
            'numerical_info': {
                'prompt': '''Extract the following information. 
                Respond in JSON format:
                {
                    "group_work_time": "percentage (0-100) or empty if not found",
                    "lecture_time": "percentage (0-100) or empty if not found",
                    "lecture_duration": "maximum duration in minutes or empty if not found"
                }''',
                'mapping': {
                    'group_work_time': 'Q21',
                    'lecture_time': 'Q22',
                    'lecture_duration': 'Q23'
                }
            }
        }

        # Process structured information first
        for info_type, details in extraction_prompts.items():
            response = amplify_chat(details['prompt'], content)
            if response and 'message' in response:
                try:
                    info = json.loads(response['message'])
                    for key, q_num in details['mapping'].items():
                        if info.get(key):
                            st.session_state.answers[q_num] = info[key]
                            st.session_state.auto_filled.add(q_num)
                            st.write(f'Found {key}: {info[key]}')
                except json.JSONDecodeError:
                    st.error(f'Error parsing {info_type}')

        # Process yes/no and frequency questions
        analysis_prompts = {
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
            'Q19': 'Are grading guides or rubrics mentioned?',
            'Q24': 'Look for frequency of demonstrations/simulations/videos usage. Respond with one of: every class, every week, once in a while, rarely',
            'Q25': 'Are specific instructions for video viewing and follow-up discussions mentioned?',
            'Q26': 'Look for frequency of discussing material usefulness. Respond with one of: every class, every week, once in a while, rarely',
            'Q27': 'Is use of response system for ungraded activities mentioned?',
            'Q28': 'Is use of response system for graded activities mentioned?',
            'Q29': 'Are ungraded homework/practice problems mentioned?',
            'Q30': 'Are graded homework/problems mentioned?',
            'Q31': 'Are projects/papers with topic choice mentioned?',
            'Q32': 'Is student collaboration on individual assignments mentioned?',
            'Q33': 'Are group assignments mentioned?',
            'Q34': 'Is collecting anonymous feedback during term mentioned?',
            'Q35': 'Is revision of work based on feedback mentioned?',
            'Q36': 'Is student access to graded work mentioned?',
            'Q37': 'Are answer keys mentioned?',
            'Q38': 'Is AI/LLM usage documentation requirement mentioned?',
            'Q39': 'Are student progress meetings mentioned?',
            'Q40': 'Is initial knowledge assessment mentioned?',
            'Q41': 'Is pre-and-post testing mentioned?',
            'Q42': 'Is assessment of student interest/feelings mentioned?',
            'Q43': 'Is student choice in learning/grading mentioned?',
            'Q44': 'Look for mentions of trying new teaching methods. Respond with: often, sometimes, rarely',
            'Q45': 'Are TAs or LAs mentioned?',
            'Q46': 'Is TA/LA training mentioned?',
            'Q47': 'Are regular TA/LA meetings mentioned?',
            'Q48': 'Is use of other instructors\' materials mentioned?',
            'Q49': 'Is material sharing among instructors mentioned?',
            'Q50': 'Is discussion with colleagues about teaching mentioned?',
            'Q51': 'Are teaching workshops or articles mentioned?',
            'Q52': 'Is observation of other instructors\' classes mentioned?'
        }

        for q_key, prompt in analysis_prompts.items():
            response = amplify_chat(prompt, content)
            if response and 'message' in response:
                answer = response['message'].strip().lower()
                valid_answer = False
                
                if q_key in ['Q24', 'Q26']:  # Frequency questions
                    valid_options = ['every class', 'every week', 'once in a while', 'rarely']
                    if answer in valid_options:
                        valid_answer = True
                elif q_key == 'Q44':  # Often/sometimes/rarely
                    valid_options = ['often', 'sometimes', 'rarely']
                    if answer in valid_options:
                        valid_answer = True
                else:  # Yes/no questions
                    if answer in ['y', 'n']:
                        valid_answer = True
                
                if valid_answer:
                    st.session_state.answers[q_key] = answer
                    st.session_state.auto_filled.add(q_key)
                    st.write(f'Found answer for {q_key}: {answer}')

        # Show summary of what was found
        num_found = len(st.session_state.auto_filled)
        if num_found > 0:
            st.success(f'Successfully pre-filled {num_found} answers from your document. Please review and modify if needed.')
        else:
            st.warning('Could not automatically extract any answers from the document. Please fill in the questions manually.')

def save_response(answers):
    """Save answers to Streamlit's built-in storage"""
    try:
        # Create a record with timestamp
        from datetime import datetime
        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **answers  # Include all answers
        }
        
        # Get existing responses or initialize empty list
        if 'stored_responses' not in st.session_state:
            st.session_state.stored_responses = []
        
        # Add new response
        st.session_state.stored_responses.append(record)
        
        return True
    except Exception as e:
        st.error(f'Error saving response: {str(e)}')
        return False
    
def main():
    sections = {
        'I: Course Details': range(1, 5),
        'II: Information Provided to Students': range(5, 9),
        'III: Supporting Materials': range(9, 20),
        'IV: In-Class Features': range(20, 29),
        'V: Assignments': range(29, 34),
        'VI: Feedback and Testing': range(34, 40),
        'VII: Other': range(40, 45),
        'VIII: TAs and LAs': range(45, 48),
        'IX: Collaboration': range(48, 53)
    }

    # Welcome screen and file upload
    if st.session_state.current_step == 'welcome':
        st.title('Psychology Department Teaching Inventory')
        st.write("""
        The full inventory has several questions but I want to help you answer them as fast as possible. 
        If you have a syllabus for the course, or any other document relevant to your teaching practices 
        in this course, please upload it.
        """)
        
        uploaded_files = st.file_uploader(
            'Upload your syllabus or other relevant documents', 
            accept_multiple_files=True,
            type=['pdf', 'txt']
        )
        
        if st.button('Continue'):
            if uploaded_files:
                for file in uploaded_files:
                    if file.type == 'application/pdf':
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
        st.title('Course Information')
        
        # Progress bar
        total_questions = 52
        answered_questions = len([k for k in st.session_state.answers.keys() if st.session_state.answers[k] != ''])
        progress = answered_questions / total_questions
        st.progress(progress)
        st.write(f'Progress: {answered_questions}/{total_questions} questions answered')
        
        for section, q_range in sections.items():
            st.header(section)
            for i in q_range:
                q_key = f'Q{i}'
                
                # Text input for first four questions
                if i <= 4:
                    text_input_field(q_key, QUESTIONS[q_key])
                
                # Percentage sliders
                elif i in [21, 22]:
                    number_input_field(q_key, QUESTIONS[q_key], 0, 100, 'percentage')
                
                # Duration input
                elif i == 23:
                    number_input_field(q_key, QUESTIONS[q_key], 0, 180, 'minutes')
                
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
            
            st.markdown('---')

        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.button('Submit', type='primary')
        
        if submit_button:
    with st.spinner('Saving your responses...'):
        if save_response(st.session_state.answers):
            # Save the data to a CSV file
            if 'stored_responses' in st.session_state:
                import pandas as pd
                df = pd.DataFrame(st.session_state.stored_responses)
                df.to_csv('responses.csv', index=False)
                st.write("Responses saved to responses.csv")

            feedback_prompt = '''
            Based on the syllabus content provided, what are the most important items 
            that could be added to make the syllabus more comprehensive? Focus on items 
            that weren't found in the current syllabus. Keep the response brief and constructive.
            '''
            
            feedback_response = amplify_chat(feedback_prompt, st.session_state.uploaded_files_content)

            st.success('Thank you for completing the inventory!')
            if feedback_response and 'message' in feedback_response:
                st.info(feedback_response['message'])

            # Reset for next use
            st.session_state.current_step = 'welcome'
            st.session_state.answers = {}
            st.session_state.uploaded_files_content = ''
            st.session_state.auto_filled = set()
            st.rerun()

if __name__ == "__main__":
    main()