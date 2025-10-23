import requests

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

payload = {
    "model": "google/gemini-2.5-flash-preview-image",
    "messages": [
        {
            "role": "user",
            "content": "Hello"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")