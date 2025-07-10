#!/usr/bin/env python
"""
Flask Web Application for Sex Education Chatbot
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import traceback
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import SexEducatorChatbot

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global chatbot instance
chatbot = None

def get_chatbot():
    """Get or create chatbot instance"""
    global chatbot
    if chatbot is None:
        try:
            chatbot = SexEducatorChatbot()
            logger.info("Chatbot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            raise
    return chatbot

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get chatbot instance
        bot = get_chatbot()
        
        # Process the message
        response = bot.process_user_input(user_message)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Sorry, I encountered an error processing your message. Please try again.',
            'status': 'error'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        bot = get_chatbot()
        return jsonify({
            'status': 'healthy',
            'chatbot': 'initialized'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation history"""
    try:
        bot = get_chatbot()
        bot.memory.messages = []
        bot.memory.user_profile = {}
        bot.memory.sensitive_topics = []
        
        return jsonify({
            'status': 'success',
            'message': 'Conversation reset successfully'
        })
    except Exception as e:
        logger.error(f"Reset error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def create_app():
    """Application factory"""
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=False, host='0.0.0.0', port=port)