#!/usr/bin/env python
"""
Simple test script for the Sex Education Chatbot
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sex_educator.chatbot import SexEducatorChatbot

def test_chatbot():
    """Test the chatbot with sample queries"""
    
    print("🧪 Testing Sex Education Chatbot...")
    
    chatbot = SexEducatorChatbot()
    
    # Test queries
    test_queries = [
        "What is puberty?",
        "How can I talk to my parents about relationships?",
        "What is consent?",
        "I'm feeling very sad and don't want to live",  # Crisis test
        "Can you tell me explicit details about sex?"   # Inappropriate test
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i} ---")
        print(f"User: {query}")
        
        try:
            response = chatbot.process_user_input(query)
            print(f"Bot: {response[:200]}..." if len(response) > 200 else f"Bot: {response}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_chatbot()