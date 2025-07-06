import os
import requests
import random
import json

# Get the API key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

def get_fraud_detection_response(message):
    """Get a relevant response for fraud detection questions"""
    message_lower = message.lower()
    
    # Risk score related questions
    if any(word in message_lower for word in ['risk score', 'risk', 'score']):
        return """📊 **Risk Score Explanation**

The risk score is a numerical value between 0 and 1 that indicates the likelihood of a transaction being fraudulent:

• **0.0 - 0.3**: Low risk (likely legitimate)
• **0.3 - 0.7**: Medium risk (needs review)
• **0.7 - 1.0**: High risk (likely fraudulent)

**How it's calculated:**
- Machine learning algorithms analyze transaction patterns
- Considers factors like amount, location, time, and user behavior
- Higher scores indicate more suspicious characteristics

**What to do:**
- Scores above 0.7 should be manually reviewed
- Scores below 0.3 are usually safe to approve
- Always consider context and additional verification for medium scores"""

    # Fraud detection questions
    elif any(word in message_lower for word in ['fraud', 'fraudulent', 'detect']):
        return """🔍 **Fraud Detection System**

Our AI-powered fraud detection system analyzes transactions using:

**Key Features:**
• **Pattern Recognition**: Identifies unusual transaction patterns
• **Machine Learning**: Learns from historical fraud data
• **Real-time Analysis**: Processes transactions instantly
• **Risk Scoring**: Assigns probability scores to each transaction

**Common Fraud Indicators:**
• Unusual transaction amounts
• Transactions from new locations
• Multiple rapid transactions
• Mismatched cardholder information
• Suspicious merchant categories

**Best Practices:**
• Review high-risk transactions manually
• Monitor for patterns over time
• Keep fraud detection models updated
• Train staff on fraud recognition"""

    # General help questions
    elif any(word in message_lower for word in ['help', 'how', 'what']):
        return """🤖 **AI Fraud Detection Assistant**

I'm here to help you understand your fraud detection results! You can ask me about:

**📊 Risk Scores**
• What the risk score means
• How to interpret different score ranges
• When to take action based on scores

**🔍 Fraud Detection**
• How our system works
• Common fraud indicators
• Best practices for monitoring

**📈 Results Analysis**
• Understanding transaction flags
• Interpreting detection patterns
• Improving detection accuracy

**💡 Tips**
• Always review high-risk transactions
• Monitor patterns over time
• Keep your fraud detection updated

What specific aspect would you like to know more about?"""

    # Transaction analysis questions
    elif any(word in message_lower for word in ['transaction', 'result', 'analysis']):
        return """📈 **Transaction Analysis**

When analyzing transaction results, focus on:

**Key Metrics:**
• **Risk Score**: Primary indicator of fraud probability
• **Transaction Amount**: Unusual amounts may indicate fraud
• **Location**: Transactions from unexpected locations
• **Timing**: Rapid or unusual transaction timing
• **Merchant Type**: Suspicious merchant categories

**Action Items:**
• **High Risk (0.7+)**: Immediate review and potential blocking
• **Medium Risk (0.3-0.7)**: Additional verification recommended
• **Low Risk (0.0-0.3)**: Usually safe to approve

**Review Process:**
1. Check transaction details
2. Verify with customer if needed
3. Look for patterns across multiple transactions
4. Update fraud detection rules if necessary

Would you like me to explain any specific aspect of transaction analysis?"""

    # Default response
    else:
        responses = [
            "I'm here to help with fraud detection questions. Could you be more specific about what you'd like to know?",
            "For fraud detection assistance, please ask about risk scores, transaction analysis, or fraud indicators.",
            "I can help explain risk scores, fraud detection methods, or transaction analysis. What interests you?",
            "Let me know if you have questions about fraud detection, risk assessment, or transaction monitoring."
        ]
        return random.choice(responses)

def ask_gemini(message):
    """Get real-time response from Google Gemini API"""
    
    # Check if API key is available
    if not GEMINI_API_KEY:
        return "❌ **Configuration Error**\n\nGemini API key not found. Please check your environment variables."
    
    # Gemini API endpoint (corrected URL)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Format the message for fraud detection context
    formatted_message = f"""You are an AI assistant for a fraud detection system. Please provide helpful, accurate responses about fraud detection, risk scores, transaction analysis, and related topics.

User question: {message}

Please provide a clear, helpful response focused on fraud detection and financial security."""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": formatted_message
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500,
            "topP": 0.8,
            "topK": 40
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    if 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content']:
                        if len(data['candidates'][0]['content']['parts']) > 0:
                            return data['candidates'][0]['content']['parts'][0]['text']
                
                # Fallback if response format is different
                return "I'm here to help with fraud detection questions. Could you please ask something specific about risk scores, transaction analysis, or fraud indicators?"
                
            except Exception as e:
                return "I'm here to help with fraud detection questions. Could you please ask something specific about risk scores, transaction analysis, or fraud indicators?"
                
        elif response.status_code == 400:
            return "❌ **Invalid Request**\n\nPlease check your API configuration."
        elif response.status_code == 401:
            return "❌ **Authentication Error**\n\nInvalid API key. Please check your Gemini API key."
        elif response.status_code == 403:
            return "❌ **Access Denied**\n\nAPI key doesn't have permission for this service."
        elif response.status_code == 404:
            return "❌ **Model Not Found**\n\nThe AI model is currently unavailable. Please try again later."
        elif response.status_code == 429:
            return "🤖 **Rate Limit Reached**\n\nToo many requests. Please wait a moment and try again."
        else:
            return f"❌ **API Error {response.status_code}**\n\nResponse: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "⏰ **Request Timeout**\n\nThe AI service is taking too long to respond. Please try again."
    except Exception as e:
        return "❌ **Connection Error**\n\nUnable to connect to AI service. Please try again."

# Keep the old function name for compatibility
def ask_huggingface(message):
    """Wrapper function to maintain compatibility with existing code"""
    return ask_gemini(message)

# Main function for Gemini API
def ask_gemini_api(message):
    """Main function for Gemini API calls"""
    return ask_gemini(message)
