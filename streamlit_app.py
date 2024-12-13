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
    
    # Modified content structure
    payload = {
        "data": {
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Hello, can you hear me?"
                    }
                }
            ],
            "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "assistant_id": st.secrets["AMPLIFY_ASSISTANT_ID"],
            "temperature": 0.7,
            "max_tokens": 500,
            "options": {
                "ragOnly": False,
                "skipRag": True
            }
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
            response_json = response.json()
            st.write("Parsed Response:", response_json)
            
            if isinstance(response_json, dict):
                if response_json.get('success') == False:
                    st.error(f"API Error: {response_json.get('message')}")
                else:
                    st.success("API call successful!")
                    if 'data' in response_json:
                        st.write("Response data:", response_json['data'])
                    else:
                        st.write("Full response:", response_json)
            else:
                st.error(f"Unexpected response format: {response_json}")
        
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

if __name__ == "__main__":
    main()