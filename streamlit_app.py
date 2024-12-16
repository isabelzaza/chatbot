import requests
import json
import streamlit as st
import PyPDF2
import docx
import io

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
        # Convert the uploaded file to bytes
        file_bytes = uploaded_file.getvalue()
        
        # Process based on file type
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

def make_llm_request(messages, file_content=None):
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

    # If there's file content, add it to the messages
    if file_content:
        messages = [
            {
                "role": "system",
                "content": f"Here is the content of the uploaded document:\n\n{file_content}"
            }
        ] + messages

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
                "prompt": messages[0]["content"] if messages else "",
            },
        }
    }

    try:
        with st.spinner('Waiting for response...'):
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
    st.title("Document Q&A Interface")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a document (PDF or Word)", 
                                   type=["pdf", "docx"])
    
    # Process the file if uploaded
    file_content = None
    if uploaded_file:
        with st.spinner('Processing document...'):
            file_content = process_uploaded_file(uploaded_file)
            if file_content:
                st.success("Document processed successfully!")
                if st.checkbox("Show document content"):
                    st.text_area("Document content:", file_content, height=200)
    
    # Create a text input for the user's prompt
    user_prompt = st.text_area(
        "Enter your question about the document:",
        "Please summarize the main points of this document."
    )
    
    # Create a button to submit the query
    if st.button("Submit"):
        if not uploaded_file:
            st.warning("Please upload a document first.")
        elif user_prompt:
            messages = [
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ]
            
            # Make the request and get the response
            response = make_llm_request(messages, file_content)
            
            # Display the response
            if response:
                st.subheader("Response:")
                st.write(response)
        else:
            st.warning("Please enter a question before submitting.")

if __name__ == "__main__":
    main()