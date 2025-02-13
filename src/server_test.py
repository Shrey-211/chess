import requests
import json

def query_ollama(model: str, prompt: str):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json().get("response", "No response received")
    else:
        return f"Error: {response.status_code}, {response.text}"

if __name__ == "__main__":
    model_name = "llama3.2:latest"
    user_prompt = "how good are you in chess?"
    reply = query_ollama(model_name, user_prompt)
    print("Ollama Response:", reply)
