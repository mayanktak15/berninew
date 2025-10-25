#!/usr/bin/env python3
"""
Test the chatbot fixes for the Google API key issue
"""
import os
import sys

def test_chatbot_functions():
    """Test chatbot functions to verify fixes"""
    print("=== Testing Chatbot Functions ===")
    
    try:
        # Test imports
        print("1. Testing imports...")
        from evaluate_different_modules import (
            get_simple_faq_response, 
            process_query5, 
            GENAI_AVAILABLE, 
            api_key
        )
        print("✅ All imports successful!")
        
        # Check API key status
        print(f"2. API Key status: {api_key[:10] if api_key else 'None'}...")
        print(f"   GENAI_AVAILABLE: {GENAI_AVAILABLE}")
        
        # Test simple FAQ response
        print("3. Testing simple FAQ response...")
        test_queries = ["diabetes", "fever", "what is docify", "hello"]
        
        for query in test_queries:
            response = get_simple_faq_response(query)
            print(f"   Query: '{query}' -> Response: {response[:80]}...")
        
        print("✅ Simple FAQ responses working!")
        
        # Test process_query5 (should fall back gracefully)
        print("4. Testing process_query5 with fallback...")
        for query in test_queries:
            response = process_query5(query)
            print(f"   Query: '{query}' -> Response: {response[:80]}...")
        
        print("✅ process_query5 working with fallback!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_curl_test_commands():
    """Generate curl commands for testing the API endpoint"""
    print("\n=== CURL Test Commands for Azure VM ===")
    
    test_queries = [
        {"message": "diabetes"},
        {"message": "fever"},
        {"message": "what is docify"},
        {"message": "hello"}
    ]
    
    for query in test_queries:
        print(f"""
# Test query: {query['message']}
curl -X POST -H "Content-Type: application/json" \\
     -d '{{"message": "{query["message"]}"}}' \\
     http://YOUR_VM_IP:5000/chatbot
""")

if __name__ == "__main__":
    success = test_chatbot_functions()
    
    if success:
        print("\n✅ All tests passed! The chatbot should work properly now.")
        create_curl_test_commands()
    else:
        print("\n❌ Tests failed. Check the error messages above.")
    
    print("\n=== Instructions for Azure VM ===")
    print("1. Upload the updated evaluate_different_modules.py to your Azure VM")
    print("2. Restart your Flask application: pkill -f 'python.*app.py' && nohup python3 app.py &")
    print("3. Test with the curl commands shown above")
    print("4. The chatbot should now work with fallback responses even without a valid Google API key")
