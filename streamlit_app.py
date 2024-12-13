import streamlit as st
import requests
import json

# Configure page
st.set_page_config(page_title="API Test", layout="wide")

def test_api(user_message="Tell me about vanderbilt university"):
    """Simple test of Amplify API with streaming support"""
    url = "https://prod-api.vanderbilt.ai/chat"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['AMPLIFY_API_KEY']}",
        "Accept": "text/event-stream"
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
                "stream": True
            }
        }
    }
    
    try:
        st.write("Making API call...")
        st.write("Headers:", {k:v for k,v in headers.items() if k != 'Authorization'})
        st.write("Payload:", json.dumps(payload, indent=2))
        
        # Create a placeholder for the streaming response
        response_placeholder = st.empty()
        debug_placeholder = st.empty()
        full_response = ""
        
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            st.write("Response Status:", response.status_code)
            
            if response.status_code == 200:
                st.write("Starting to read response...")
                
                for chunk in response.iter_lines():
                    if chunk:
                        # Debug: show raw chunk
                        debug_placeholder.write(f"Raw chunk: {chunk.decode('utf-8')}")
                        
                        try:
                            # Try to parse as JSON
                            chunk_data = json.loads(chunk.decode('utf-8'))
                            st.write("Chunk data:", chunk_data)
                            
                            # Check different possible response formats
                            if isinstance(chunk_data, dict):
                                if 'data' in chunk_data:
                                    text = chunk_data['data']
                                    full_response += text
                                elif 'message' in chunk_data:
                                    text = chunk_data['message']
                                    full_response += text
                                
                                response_placeholder.write(f"Current response: {full_response}")
                                
                        except json.JSONDecodeError as e:
                            st.write(f"Chunk is not JSON: {chunk.decode('utf-8')}")
                            # If it's not JSON, try to use the raw text
                            text = chunk.decode('utf-8')
                            if text.startswith('data: '):
                                text = text[6:]  # Remove 'data: ' prefix
                            full_response += text
                            response_placeholder.write(f"Current response: {full_response}")
                
                if full_response:
                    st.success("Stream completed successfully!")
                    st.write("Final response:", full_response)
                else:
                    st.warning("Stream completed but no content received")
                    
                # Try reading the response one more time as regular JSON
                try:
                    final_response = response.json()
                    st.write("Final JSON response:", final_response)
                except Exception as e:
                    st.write("Could not parse final response as JSON")
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
    st.title("Amplify API Test (Debug Streaming)")
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
    - This version includes detailed debugging information
    - You'll see the raw chunks of data as they arrive
    - Watch for both the streaming updates and final response
    """)

if __name__ == "__main__":
    main()