import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
import io

# Configure page
st.set_page_config(page_title="API Test", layout="wide")

def test_api():
    """Simple test of Amplify API"""
    url = "https://prod-api.vanderbilt.ai/chat"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.secrets["AMPLIFY_API_KEY"]}'
    }
    
    # Simplified message structure
    payload = {
        "data": {
            "message": "Hello, can you hear me?",
            "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "assistant_id": st.secrets["AMPLIFY_ASSISTANT_ID"],
            "temperature": 0.7,
            "max_tokens": 500,
            "system_message": "You are a helpful assistant."
        }
    }
    
    try:
        st.write("Making API call...")
        st.write("Headers:", {k:v for k,v in headers.items() if k != 'Authorization'})
        st.write("Payload:", json.dumps(payload, indent=2))
        
        response = requests.post(url, headers=headers, json=payload)
        
        st.write("Response Status:", response.status_code)
        st.write("Raw Response:", response.text)
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                st.write("Parsed Response:", response_json)
                
                if isinstance(response_json, dict):
                    if response_json.get('success') == False:
                        st.error(f"API Error: {response_json.get('message')}")
                        st.write("Would you be able to share any example of a working API call to this endpoint?")
                    else:
                        st.success("API call successful!")
                        st.write("Full response:", response_json)
                else:
                    st.error(f"Unexpected response format: {response_json}")
                    
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse response as JSON: {e}")
                st.write("Raw response was:", response.text)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Exception details:", {
            "type": type(e).__name__,
            "str": str(e),
            "repr": repr(e)
        })

def main():
    st.title("Amplify API Test")
    st.write("Available secrets:", list(st.secrets.keys()))
    st.write("API Key length:", len(st.secrets["AMPLIFY_API_KEY"]))
    
    if st.button("Test API Connection"):
        test_api()
    
    st.write("""
    Note: To help debug this further, it would be very helpful to have:
    1. A working example of an API call
    2. The server-side error logs
    3. API documentation showing the expected format
    """)

if __name__ == "__main__":
    main()