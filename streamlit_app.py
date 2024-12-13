import streamlit as st
import requests
import json
import sseclient

# Configure page
st.set_page_config(page_title="API Test", layout="wide")

def test_api(user_message="Tell me about vanderbilt university"):
    """Simple test of Amplify API with streaming support"""
    url = "https://prod-api.vanderbilt.ai/chat"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['AMPLIFY_API_KEY']}",
        "Accept": "text/event-stream"  # Add header for SSE
    }
    
    payload = {
        "data": {
            "model": "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "temperature": 0.7,
            "max_tokens": 500,
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
                "assistantId": st.secrets["AMPLIFY_ASSISTANT_ID"],
                "stream": True  # Enable streaming
            }
        }
    }
    
    try:
        st.write("Making API call...")
        st.write("Headers:", {k:v for k,v in headers.items() if k != 'Authorization'})
        st.write("Payload:", json.dumps(payload, indent=2))
        
        # Create a placeholder for the streaming response
        response_placeholder = st.empty()
        full_response = ""
        
        # Make streaming request
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            st.write("Response Status:", response.status_code)
            
            if response.status_code == 200:
                client = sseclient.SSEClient(response)
                
                # Process the stream
                for event in client.events():
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            if isinstance(data, dict):
                                chunk = data.get('data', '')
                                if chunk:
                                    full_response += chunk
                                    response_placeholder.write(f"Response: {full_response}")
                        except json.JSONDecodeError:
                            # Handle raw text chunks
                            full_response += event.data
                            response_placeholder.write(f"Response: {full_response}")
                
                if full_response:
                    st.success("Stream completed successfully!")
                else:
                    st.warning("Stream completed but no content received")
            else:
                st.error(f"Error: Status code {response.status_code}")
                st.write("Response content:", response.text)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.write("Exception details:", {
            "type": type(e).__name__,
            "args": e.args,
            "str": str(e)
        })

def main():
    st.title("Amplify API Test (Streaming)")
    st.write("Available secrets:", list(st.secrets.keys()))
    st.write("API Key length:", len(st.secrets["AMPLIFY_API_KEY"]))
    
    user_message = st.text_input(
        "Enter your message (optional):", 
        "Tell me about vanderbilt university"
    )
    
    if st.button("Test API Connection"):
        test_api(user_message)
    
    st.write("""
    Note: 
    - This version supports streaming responses
    - Watch for real-time updates as the response comes in
    - The response will appear in the placeholder above
    """)

if __name__ == "__main__":
    main()