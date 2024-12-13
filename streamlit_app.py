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
    
    # Updated payload with messages array
    payload = {
        "data": {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, can you hear me?"
                }
            ],
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
        
        if response.status_code == 200:
            st.success("API call successful!")
            st.json(response.json())
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

def main():
    st.title("Amplify API Test")
    
    # Display the secrets we're using (without showing actual values)
    st.write("Available secrets:", list(st.secrets.keys()))
    
    if st.button("Test API Connection"):
        test_api()

if __name__ == "__main__":
    main()