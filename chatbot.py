from dotenv import load_dotenv
import os
import requests

load_dotenv()
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')
HF_MODEL = 'bigscience/bloomz-560m'
HF_API_URL = f'https://api-inference.huggingface.co/models/{HF_MODEL}'

def ask_huggingface(message):
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    payload = {
        "inputs": message,
        "options": {"wait_for_model": True}
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
            return data[0]['generated_text']
        else:
            return '[Error: No generated_text in response]'
    else:
        return f"[Error: {response.status_code} - {response.text}]"
