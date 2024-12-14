import streamlit as st
import requests
import json

# Configure page
st.set_page_config(page_title="API Test", layout="wide")

def get_assistant_info():
    """Get information about available assistants"""
    url = "https://prod-api.vanderbilt.ai/assistant/list"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['AMPLIFY_API_KEY']}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        st.write("Assistant List Response Status:", response.status_code)
        st.write("Assistant List Response:", response.text)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Error getting assistant info: {str(e)}")
        return None

def test_api(user_message="Tell me about vanderbilt university", selected_model="anthropic.claude-3-5-sonnet-20240620-v1:0"):
    """Simple test of Amplify API"""
    url = "https://prod-api.vanderbilt.ai/chat"
    
    # First, get assistant info
    st.write("Checking assistant configuration...")
    assistant_info = get_assistant_info()
    if assistant_info:
        st.write("Found assistant information:", assistant_info)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['AMPLIFY_API_KEY']}"
    }
    
    payload = {
        "data": {
            "model": selected_model,
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
                "assistantId": "astp/a55270be-f801-4a28-afc0-38ba9290ef10",
                "dataSourceOptions": {
                    "includeAttachedDocumentsInPrompt": True,
                    "includeConversationDocumentsInRAG": True,
                    "allowAssistantToCreateArtifacts": True
                }
            }
        }
    }
    
    st.write("Assistant ID being used:", payload["data"]["options"]["assistantId"])
    
    try:
        st.write("Making chat API call...")
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
                        No data in response. Possible issues:
                        1. Assistant might need configuration
                        2. Assistant might not have correct permissions
                        3. Model might not be enabled for this assistant
                        
                        Try checking the assistant configuration in the UI or creating a new assistant.
                        """)
                        st.write("Full response object:", response_json)
                else:
                    st.error(f"API Error: {response_json.get('message', 'Unknown error')}")
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse response as JSON: {e}")
                st.write("Raw response was:", response.text)
        else:
            st.error(f"Error Response: {response.text}")
            
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
        test_api(user_message, selected_model)
        
    st.write("""
    Notes:
    - Added assistant list check
    - Verifying assistant configuration
    - Will show assistant details if found
    """)

if __name__ == "__main__":
    main()