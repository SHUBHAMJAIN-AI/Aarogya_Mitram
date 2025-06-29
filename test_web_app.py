#!/usr/bin/env python
"""
Test script for the Sex Education Chatbot Web Application
"""

import sys
import os
import threading
import time
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sex_educator.web_app import app

def test_web_app():
    """Test the web application endpoints"""
    
    print("🧪 Testing Sex Education Chatbot Web Application...")
    
    # Start the Flask app in a separate thread
    def run_app():
        app.run(debug=False, host='127.0.0.1', port=5001, use_reloader=False)
    
    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Test 1: Health check
        print("\n--- Test 1: Health Check ---")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
        
        # Test 2: Main page
        print("\n--- Test 2: Main Page ---")
        response = requests.get(base_url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page error: {response.text}")
        
        # Test 3: Chat API
        print("\n--- Test 3: Chat API ---")
        chat_data = {"message": "What is puberty?"}
        response = requests.post(f"{base_url}/api/chat", json=chat_data, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', '')[:100]}...")
        else:
            print(f"Error: {response.text}")
        
        # Test 4: Reset API
        print("\n--- Test 4: Reset API ---")
        response = requests.post(f"{base_url}/api/reset", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
        
        print("\n✅ Web application testing completed!")
        print(f"🌐 You can access the web interface at: {base_url}")
        print("📱 Open this URL in your browser to use the chatbot")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the web server")
        print("Make sure all dependencies are installed:")
        print("pip install flask flask-cors")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_web_app()