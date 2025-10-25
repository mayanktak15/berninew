#!/usr/bin/env python3
"""
Test script to verify chatbot functionality with API key handling
"""
import os
import sys

# Add current directory to path for imports
sys.path.append('.')

def test_api_key_handling():
    """Test the API key handling in evaluate_different_modules"""
    print("Testing API key handling...")
    
    try:
        from evaluate_different_modules import api_key, GENAI_AVAILABLE, get_simple_faq_response
        print(f"API key loaded: {api_key[:10] if api_key else 'None'}...")
        print(f"GENAI_AVAILABLE: {GENAI_AVAILABLE}")
        
        # Test simple FAQ response
        test_query = "hy"
        response = get_simple_faq_response(test_query)
        print(f"Simple FAQ response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"Error testing API key handling: {e}")
        return False

def test_process_query5():
    """Test the process_query5 function specifically"""
    print("\nTesting process_query5...")
    
    try:
        from evaluate_different_modules import process_query5
        
        test_query = "hy"
        response = process_query5(test_query)
        print(f"process_query5 response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"Error testing process_query5: {e}")
        return False

if __name__ == "__main__":
    print("=== Chatbot API Key Test ===")
    
    # Test 1: API key handling
    success1 = test_api_key_handling()
    
    # Test 2: process_query5 function
    success2 = test_process_query5()
    
    if success1 and success2:
        print("\n✅ All tests passed! Chatbot should work now.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
    
    print("\n=== Test Complete ===")
