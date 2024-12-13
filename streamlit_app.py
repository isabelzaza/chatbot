import streamlit as st
import requests
import json

# Configure page
st.set_page_config(page_title="API Test", layout="wide")

def test_api():
    """Simple test of Amplify API"""
    url = "https://prod-api.vanderbilt.ai/chat"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {st.secrets["AMPLIFY_API_KEY"]}'
    }
    
    # Minimal test payload
    payload = {
        "data": {
            "message": "Hello, can you hear me?",
            "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "temperature": 0.7,
            "max_tokens": 500,
            "assistant_id": st.secrets["AMPLIFY_ASSISTANT_ID"]
        }
    }
    
    try:
        st.write("Making API call...")
        st.write("Headers:", {k:v for k,v in headers.items() if k != 'Authorization'})
        st.write("Payload:", json.dumps(payload, indent=2))
        
        response = requests.post(url, headers=headers, json=payload)
        
        st.write("Response Status:", response.status_code)
        st.write("Response Headers:", dict(response.headers))
        st.write("Response Content:", response.text)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

def main():
    st.title("Amplify API Test")
    
    if st.button("Test API Connection"):
        test_api()

if __name__ == "__main__":
    main()