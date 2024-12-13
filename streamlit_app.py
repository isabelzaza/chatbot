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
    
    # Modified payload with model in options
    payload = {
        "data": {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
            "dataSources": [],
            "options": {
                "ragOnly": False,
                "skipRag": True,
                "model": ["anthropic.claude-3-5-sonnet-20240620-v1:0"],  # Changed to array format
                "assistantId": st.secrets["AMPLIFY_ASSISTANT_ID"],
                "prompt": user_message
            }
        }
    }
    
    # Debug info about the assistant ID
    st.write("Assistant ID being used:", st.secrets["AMPLIFY_ASSISTANT_ID"])
    
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
                        st.warning("""
                        No data in response. This could mean:
                        1. The assistant ID might need validation
                        2. The model specification might need adjustment
                        3. We might need additional permissions
                        
                        Consider:
                        1. Verifying the assistant ID in the Amplify dashboard
                        2. Checking if the assistant has the necessary permissions
                        3. Testing a different model from the allowed list
                        """)
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
    
    # Add model selection
    model_options = [
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "gpt-35-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        "mistral.mistral-7b-instruct-v0:2"
    ]
    selected_model = st.selectbox("Select Model", model_options)
    
    user_message = st.text_input(
        "Enter your message (optional):", 
        "Tell me about vanderbilt university"
    )
    
    if st.button("Test API Connection"):
        test_api(user_message)
        
    st.write("""
    Notes:
    - Added model selection dropdown
    - Moved model specification to options
    - Changed model format to array
    - Added more debugging information
    """)

if __name__ == "__main__":
    main()