from openai import OpenAI

client = OpenAI(api_key="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")

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print(response)
except Exception as e:
    print(f"Error: {e}")