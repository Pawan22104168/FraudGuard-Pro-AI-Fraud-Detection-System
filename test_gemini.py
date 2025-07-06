import os
import requests
import json

def test_gemini_api():
    """Test the Gemini API functionality"""
    
    # Get API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY', '')
    
    if not api_key:
        print("❌ No Gemini API key found in environment variables")
        print("Please set GEMINI_API_KEY environment variable")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Test message
    test_message = "Hello, can you help me understand fraud detection?"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"You are an AI assistant for a fraud detection system. Please provide a brief response to: {test_message}"
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 200,
            "topP": 0.8,
            "topK": 40
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🔄 Testing Gemini API...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ API call successful!")
                
                if 'candidates' in data and len(data['candidates']) > 0:
                    if 'content' in data['candidates'][0] and 'parts' in data['candidates'][0]['content']:
                        if len(data['candidates'][0]['content']['parts']) > 0:
                            response_text = data['candidates'][0]['content']['parts'][0]['text']
                            print(f"Response: {response_text}")
                            return True
                
                print("⚠️ Unexpected response format")
                print(f"Response data: {json.dumps(data, indent=2)[:500]}...")
                return False
                
            except Exception as e:
                print(f"❌ JSON parsing error: {e}")
                return False
                
        elif response.status_code == 400:
            print("❌ Invalid Request - Check API configuration")
            return False
        elif response.status_code == 401:
            print("❌ Authentication Error - Invalid API key")
            return False
        elif response.status_code == 403:
            print("❌ Access Denied - API key doesn't have permission")
            return False
        else:
            print(f"❌ API Error {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request Timeout - API is taking too long to respond")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def test_chatbot_integration():
    """Test the chatbot integration"""
    print("\n=== Testing Chatbot Integration ===")
    
    # Import the chatbot function
    try:
        from chatbot import ask_gemini
        print("✅ Successfully imported chatbot module")
        
        # Test with a fraud detection question
        test_question = "What is a risk score in fraud detection?"
        print(f"Testing question: {test_question}")
        
        response = ask_gemini(test_question)
        print(f"Chatbot response: {response[:200]}...")
        
        if "risk score" in response.lower() or "fraud" in response.lower():
            print("✅ Chatbot is working correctly!")
            return True
        else:
            print("⚠️ Chatbot response doesn't seem relevant")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot integration error: {e}")
        return False

if __name__ == "__main__":
    print("=== Gemini API Test ===")
    
    # Test 1: Direct API call
    api_success = test_gemini_api()
    
    # Test 2: Chatbot integration
    chatbot_success = test_chatbot_integration()
    
    print(f"\n=== Test Results ===")
    print(f"API Test: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"Chatbot Test: {'✅ PASS' if chatbot_success else '❌ FAIL'}")
    
    if api_success and chatbot_success:
        print("\n🎉 All tests passed! The chatbot is ready for deployment.")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.") 