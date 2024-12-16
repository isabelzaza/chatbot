import requests
import json
import streamlit as st

def make_llm_request(messages):
    url = "https://prod-api.vanderbilt.ai/chat"
    
    # Get API key from Streamlit secrets
    API_KEY = st.secrets["AMPLIFY_API_KEY"]

    # Headers
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    # Data payload
    payload = {
        "data": {
            "model": "gpt-4o",  # Replace with the model you want to use
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

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Check for a successful response
    if response.status_code == 200:
        # Parse the JSON response
        response_data = response.json()

        txt = response_data.get("data", "")
        print(txt)

        # Return the data entry if it exists
        return txt
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        response.raise_for_status()
        return None


if __name__ == "__main__":
    msg = [
        {
            "role": "user",
            "content": "Please provide 1 sentence brief explanation of quantum mechanics and its applications.",  # INSERT YOUR PROMPT HERE
        }
    ]
    make_llm_request(msg)
