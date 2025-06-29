"""
Aarogya Mitram - Sex Education Chatbot for Indian Context

A culturally-sensitive, AI-powered chatbot that provides accurate,
age-appropriate sex education information adapted for Indian users.

Features:
- Multi-agent AI system using CrewAI
- Cultural adaptation for Indian context
- Crisis detection and support
- Web and CLI interfaces
- Privacy-focused design

Author: Shubham Jain
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Shubham Jain"
__description__ = "Sex Education Chatbot for Indian Context"

from .chatbot import SexEducatorChatbot
from .crew import SexEducator

__all__ = ["SexEducatorChatbot", "SexEducator"]