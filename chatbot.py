import os
import requests

# Get the token from environment variable
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')
# Using a more reliable model that's available
HF_MODEL = 'microsoft/DialoGPT-medium'
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
    
    # Check for various error conditions and show professional rate limit message
    if response.status_code in [401, 403, 404, 429, 503] or not response.text.strip():
        return """🤖 **AI Assistant Temporarily Limited**

Our AI fraud detection assistant has reached its current usage limit. This is a temporary situation while we scale our infrastructure to handle the increased demand.

**What you can do:**
• Try again in a few minutes
• Check back later today
• Contact support if you need immediate assistance

**Your fraud detection system is still fully operational** - only the AI assistant is temporarily limited.

*We're working to restore full AI assistant functionality shortly.*"""
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
                return data[0]['generated_text']
            else:
                return """🤖 **AI Assistant Temporarily Limited**

Our AI fraud detection assistant has reached its current usage limit. This is a temporary situation while we scale our infrastructure to handle the increased demand.

**What you can do:**
• Try again in a few minutes
• Check back later today
• Contact support if you need immediate assistance

**Your fraud detection system is still fully operational** - only the AI assistant is temporarily limited.

*We're working to restore full AI assistant functionality shortly.*"""
        except Exception as e:
            return """🤖 **AI Assistant Temporarily Limited**

Our AI fraud detection assistant has reached its current usage limit. This is a temporary situation while we scale our infrastructure to handle the increased demand.

**What you can do:**
• Try again in a few minutes
• Check back later today
• Contact support if you need immediate assistance

**Your fraud detection system is still fully operational** - only the AI assistant is temporarily limited.

*We're working to restore full AI assistant functionality shortly.*"""
    else:
        return """🤖 **AI Assistant Temporarily Limited**

Our AI fraud detection assistant has reached its current usage limit. This is a temporary situation while we scale our infrastructure to handle the increased demand.

**What you can do:**
• Try again in a few minutes
• Check back later today
• Contact support if you need immediate assistance

**Your fraud detection system is still fully operational** - only the AI assistant is temporarily limited.

*We're working to restore full AI assistant functionality shortly.*"""
