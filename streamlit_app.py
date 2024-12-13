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
    
    # Simplified payload based on documentation
    payload = {
        "data": {
            "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
            "dataSources": [],
            "type": "prompt",  # Added from documentation
            "options": {
                "assistantId": st.secrets["AMPLIFY_ASSISTANT_ID"],
                "prompt": user_message  # Added based on documentation
            }
        }
    }
    
    try:
        st.write("Making API call...")
        st.write("Headers:", {k:v for k,v in headers.items() if k != 'Authorization'})
        st.write("Payload:", json.dumps(payload, indent=2))
        
        response = requests.post(url, headers=headers, json=payload)
        
        st.write("Response Status:", response.status_code)
        st.write("Response Headers:", dict(response.headers))
        st.write("Raw Response:", response.text)
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                st.write("Parsed Response:", response_json)
                
                if response_json.get('success') is True:
                    response_data = response_json.get('data')
                    if response_data:
                        st.success("Got response data!")
                        st.write("Response:", response_data)
                    else:
                        st.warning("No data in response")
                        st.write("Full response object:", response_json)
                else:
                    st.error(f"API Error: {response_json.get('message', 'Unknown error')}")
                    
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
    
    user_message = st.text_input(
        "Enter your message (optional):", 
        "Tell me about vanderbilt university"
    )
    
    if st.button("Test API Connection"):
        test_api(user_message)
        
    st.write("""
    Notes:
    - Added 'type': 'prompt' from documentation
    - Added prompt in options
    - Removed streaming approach
    - Simplified payload structure
    """)

if __name__ == "__main__":
    main()