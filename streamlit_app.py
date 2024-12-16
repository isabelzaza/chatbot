import requests
import json
import streamlit as st

def make_llm_request(messages):
    url = "https://prod-api.vanderbilt.ai/chat"
    
    try:
        # Get API key from Streamlit secrets
        API_KEY = st.secrets["AMPLIFY_API_KEY"]
    except KeyError:
        st.error("API key not found in secrets. Please configure your secrets.toml file.")
        return None

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Data payload
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
            # Make the POST request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            # Check for a successful response
            if response.status_code == 200:
                # Parse the JSON response
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
    st.title("LLM Query Interface")
    
    # Create a text input for the user's prompt
    user_prompt = st.text_area(
        "Enter your prompt:",
        "Please provide 1 sentence brief explanation of quantum mechanics and its applications."
    )
    
    # Create a button to submit the query
    if st.button("Submit"):
        if user_prompt:
            messages = [
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ]
            
            # Make the request and get the response
            response = make_llm_request(messages)
            
            # Display the response
            if response:
                st.subheader("Response:")
                st.write(response)
        else:
            st.warning("Please enter a prompt before submitting.")

if __name__ == "__main__":
    main()