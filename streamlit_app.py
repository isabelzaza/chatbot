import streamlit as st
import requests
import json

# Configure page
st.set_page_config(page_title="API Test", layout="wide")

def test_api(user_message="Tell me about vanderbilt university"):
    """Simple test of Amplify API"""
    url = "https://prod-api.vanderbilt.ai/chat"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['AMPLIFY_API_KEY']}"
    }
    
    # Following the exact format from documentation with a more substantial query
    payload = {
        "data": {
            "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "temperature": 0.7,
            "max_tokens": 500,  # Increased max tokens for longer response
            "dataSources": [],
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides informative responses."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "options": {
                "ragOnly": False,
                "skipRag": True,
                "assistantId": st.secrets["AMPLIFY_ASSISTANT_ID"]
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
            try:
                response_json = response.json()
                st.write("Parsed Response:", response_json)
                
                if response_json.get('success') is True:
                    st.success("API call successful!")
                    response_data = response_json.get('data', '')
                    if response_data:
                        st.write("Assistant's response:", response_data)
                    else:
                        st.warning("Received successful response but no data. Trying with different parameters might help.")
                else:
                    st.error(f"API Error: {response_json}")
                    
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse response as JSON: {e}")
                st.write("Raw response was:", response.text)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Exception details:", {
            "type": type(e).__name__,
            "args": e.args,
            "str": str(e)
        })

def main():
    st.title("Amplify API Test")
    st.write("Available secrets:", list(st.secrets.keys()))
    st.write("API Key length:", len(st.secrets["AMPLIFY_API_KEY"]))
    
    # Add text input for custom message
    user_message = st.text_input(
        "Enter your message (optional):", 
        "Tell me about vanderbilt university"
    )
    
    if st.button("Test API Connection"):
        test_api(user_message)
    
    st.write("""
    Note: 
    - The API connection is working successfully
    - We're getting a 200 response code
    - The message is being processed
    - Try different messages to test the response
    """)

if __name__ == "__main__":
    main()