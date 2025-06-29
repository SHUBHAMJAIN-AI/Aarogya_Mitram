#!/usr/bin/env python
"""
Sex Education Chatbot Implementation
Integrates with CrewAI agents for culturally-sensitive responses
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from crewai import Agent, Task, Crew
from sex_educator.crew import SexEducator


class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 10):
        self.messages: List[Dict] = []
        self.user_profile: Dict = {}
        self.max_history = max_history
        self.sensitive_topics: List[str] = []
        
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_context(self) -> str:
        """Get conversation context for agents"""
        if not self.messages:
            return "This is the start of a new conversation."
        
        context = "Recent conversation history:\n"
        for msg in self.messages[-5:]:  # Last 5 messages
            context += f"{msg['role']}: {msg['content']}\n"
        return context
    
    def update_profile(self, key: str, value: str):
        """Update user profile information"""
        self.user_profile[key] = value


class SexEducatorChatbot:
    """Main chatbot class that orchestrates CrewAI agents"""
    
    def __init__(self):
        self.crew_system = SexEducator()
        self.memory = ConversationMemory()
        self.crisis_keywords = [
            "suicide", "self-harm", "abuse", "rape", "assault", 
            "depression", "anxiety", "panic", "help me", "emergency"
        ]
        self.inappropriate_keywords = [
            "explicit", "graphic", "detailed", "step-by-step"
        ]
        
    def detect_intent(self, user_input: str) -> str:
        """Detect user intent and categorize the query"""
        user_input_lower = user_input.lower()
        
        # Crisis detection
        if any(keyword in user_input_lower for keyword in self.crisis_keywords):
            return "crisis"
        
        # Educational categories
        if any(word in user_input_lower for word in ["anatomy", "body", "puberty", "development"]):
            return "anatomy_education"
        elif any(word in user_input_lower for word in ["relationship", "dating", "love", "partner"]):
            return "relationship_guidance"
        elif any(word in user_input_lower for word in ["contraception", "protection", "pregnancy", "std", "sti"]):
            return "health_safety"
        elif any(word in user_input_lower for word in ["consent", "boundaries", "rights", "respect"]):
            return "consent_education"
        elif any(word in user_input_lower for word in ["culture", "tradition", "family", "society"]):
            return "cultural_context"
        else:
            return "general_inquiry"
    
    def check_appropriateness(self, user_input: str) -> Tuple[bool, str]:
        """Check if the query is appropriate and provide guidance if not"""
        user_input_lower = user_input.lower()
        
        # Check for inappropriate requests
        if any(keyword in user_input_lower for keyword in self.inappropriate_keywords):
            return False, "I'm designed to provide educational information in an age-appropriate manner. I can help with general sex education topics, but I cannot provide explicit or graphic content."
        
        return True, ""
    
    def create_specialized_task(self, user_input: str, intent: str, context: str) -> Task:
        """Create a specialized task based on user intent"""
        
        task_descriptions = {
            "crisis": f"""
                URGENT: The user may be in distress. Analyze this message: "{user_input}"
                
                Context: {context}
                
                Provide immediate supportive response and escalation guidance if needed.
                Include relevant helpline numbers for India.
                """,
            
            "anatomy_education": f"""
                Provide age-appropriate, medically accurate information about: "{user_input}"
                
                Context: {context}
                
                Ensure content is culturally sensitive for Indian context and scientifically accurate.
                """,
            
            "relationship_guidance": f"""
                Provide guidance on healthy relationships regarding: "{user_input}"
                
                Context: {context}
                
                Focus on respect, communication, and cultural sensitivity in Indian context.
                """,
            
            "health_safety": f"""
                Provide health and safety information about: "{user_input}"
                
                Context: {context}
                
                Include medically accurate information and emphasize consulting healthcare providers.
                """,
            
            "consent_education": f"""
                Educate about consent and boundaries regarding: "{user_input}"
                
                Context: {context}
                
                Emphasize respect, communication, and legal aspects in Indian context.
                """,
            
            "cultural_context": f"""
                Address cultural aspects of: "{user_input}"
                
                Context: {context}
                
                Balance traditional values with comprehensive sex education principles.
                """,
            
            "general_inquiry": f"""
                Respond to this general sex education query: "{user_input}"
                
                Context: {context}
                
                Provide helpful, age-appropriate, and culturally sensitive information.
                """
        }
        
        return Task(
            description=task_descriptions.get(intent, task_descriptions["general_inquiry"]),
            expected_output="A helpful, accurate, and culturally sensitive response to the user's query.",
            agent=self._select_primary_agent(intent)
        )
    
    def _select_primary_agent(self, intent: str) -> Agent:
        """Select the most appropriate agent based on intent"""
        agent_mapping = {
            "crisis": self.crew_system.escalation_agent(),
            "anatomy_education": self.crew_system.curriculum_curator(),
            "relationship_guidance": self.crew_system.conversation_handler(),
            "health_safety": self.crew_system.curriculum_curator(),
            "consent_education": self.crew_system.legal_compliance(),
            "cultural_context": self.crew_system.cultural_adapter(),
            "general_inquiry": self.crew_system.conversation_handler()
        }
        
        return agent_mapping.get(intent, self.crew_system.conversation_handler())
    
    def process_user_input(self, user_input: str) -> str:
        """Main method to process user input and generate response"""
        
        # Add user message to memory
        self.memory.add_message("user", user_input)
        
        # Check appropriateness
        is_appropriate, inappropriate_msg = self.check_appropriateness(user_input)
        if not is_appropriate:
            self.memory.add_message("assistant", inappropriate_msg)
            return inappropriate_msg
        
        # Detect intent
        intent = self.detect_intent(user_input)
        
        # Get conversation context
        context = self.memory.get_context()
        
        # Handle crisis situations
        if intent == "crisis":
            crisis_response = self._handle_crisis_response(user_input)
            self.memory.add_message("assistant", crisis_response, {"intent": intent})
            return crisis_response
        
        try:
            # Create specialized task
            task = self.create_specialized_task(user_input, intent, context)
            
            # Create a minimal crew for this specific interaction
            agent = self._select_primary_agent(intent)
            mini_crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=False
            )
            
            # Execute the task
            result = mini_crew.kickoff()
            
            # Extract response text
            response = str(result)
            
            # Add response to memory
            self.memory.add_message("assistant", response, {"intent": intent})
            
            return response
            
        except Exception as e:
            error_response = "I apologize, but I'm having trouble processing your question right now. Could you please rephrase it or try asking something else?"
            self.memory.add_message("assistant", error_response, {"error": str(e)})
            return error_response
    
    def _handle_crisis_response(self, user_input: str) -> str:
        """Handle crisis situations with immediate support"""
        return """I'm concerned about what you've shared. Your wellbeing is important, and you don't have to face this alone.

**If you're in immediate danger, please contact:**
- Emergency Services: 112
- National Emergency Helpline: 1098 (for children)
- Women's Helpline: 1091

**For mental health support:**
- NIMHANS Helpline: 080-46110007
- Vandrevala Foundation: 9999666555
- iCall: 9152987821

**For reporting abuse:**
- Childline India: 1098
- NCW Helpline: 7827170170

Would you like to talk about something else, or would you prefer information about professional support services in your area?"""
    
    def start_conversation(self):
        """Start an interactive conversation"""
        print("🌟 Welcome to the Sex Education Chatbot! 🌟")
        print("I'm here to provide accurate, age-appropriate, and culturally sensitive information.")
        print("Feel free to ask questions about relationships, health, anatomy, or any related topics.")
        print("Type 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nThank you for using the Sex Education Chatbot. Take care! 🌸")
                    break
                
                if not user_input:
                    print("Please enter a question or type 'quit' to exit.")
                    continue
                
                response = self.process_user_input(user_input)
                print(f"\nAssistant: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Take care! 🌸")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please try again or type 'quit' to exit.")


def main():
    """Main function to run the chatbot"""
    chatbot = SexEducatorChatbot()
    chatbot.start_conversation()


if __name__ == "__main__":
    main()