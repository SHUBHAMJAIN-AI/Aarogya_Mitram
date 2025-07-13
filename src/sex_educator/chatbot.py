#!/usr/bin/env python
"""
Sex Education Chatbot Implementation
Integrates with CrewAI agents for culturally-sensitive responses
"""

import re
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from crewai import Agent, Task, Crew
from crew import SexEducator


class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 10):
        self.messages: List[Dict] = []
        self.user_profile: Dict = {}
        self.max_history = max_history
        self.sensitive_topics: List[str] = []
        self.discussed_topics: List[str] = []
        self.user_interests: List[str] = []
        self.conversation_stage: str = "greeting"  # greeting, exploring, deep_dive, wrapping_up
        self.explanation_mode: str = "normal"  # normal, bhai_mode, dad_mode
        
        # Mode definitions
        self.modes = {
            "normal": {
                "name": "Normal Mode",
                "description": "Standard educational responses",
                "style": "Professional and informative"
            },
            "bhai_mode": {
                "name": "Bhai Mode", 
                "description": "Casual, friendly explanations like talking to a close friend",
                "style": "Simple GenZ language, relatable examples, 'bro/yaar' tone"
            },
            "dad_mode": {
                "name": "Dad Mode",
                "description": "Formal, detailed explanations with legal/medical context",
                "style": "Authoritative, comprehensive, includes proper terminology"
            }
        }
        
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
    
    def add_discussed_topic(self, topic: str):
        """Track topics that have been discussed"""
        if topic not in self.discussed_topics:
            self.discussed_topics.append(topic)
    
    def set_explanation_mode(self, mode: str):
        """Set the explanation mode"""
        if mode in self.modes:
            self.explanation_mode = mode
        else:
            raise ValueError(f"Unknown mode: {mode}. Available modes: {list(self.modes.keys())}")
    
    def get_current_mode(self) -> str:
        """Get the current explanation mode"""
        return self.explanation_mode
    
    def get_mode_info(self, mode: str = None) -> Dict:
        """Get information about a specific mode or current mode"""
        mode_to_get = mode or self.explanation_mode
        return self.modes.get(mode_to_get, {})
    
    def get_mode_instruction(self) -> str:
        """Get the instruction for current mode to be used in tasks"""
        mode_info = self.get_mode_info()
        if self.explanation_mode == "bhai_mode":
            return f"\n\nIMPORTANT: Use {mode_info['name']} ({mode_info['description']}). {mode_info['style']}. Use casual Hindi-English mix where appropriate, be friendly and relatable like talking to a close friend. Use examples that GenZ can relate to."
        elif self.explanation_mode == "dad_mode":
            return f"\n\nIMPORTANT: Use {mode_info['name']} ({mode_info['description']}). {mode_info['style']}. Provide comprehensive, authoritative information with proper medical/legal terminology. Be thorough and educational."
        else:
            return ""  # Normal mode, no special instructions
    
    def get_follow_up_suggestions(self, current_intent: str, user_input: str = "") -> Dict[str, List[str]]:
        """Generate Perplexity-style categorized follow-up questions that dive deeper into the topic"""
        
        # Extract key topics from user input to generate more specific follow-ups
        user_lower = user_input.lower()
        
        # Context-aware suggestions based on recent conversation and user's specific question
        if current_intent == "anatomy_education":
            if any(word in user_lower for word in ["puberty", "changes", "development"]):
                return {
                    "Continue Learning": [
                        "What are the emotional changes during puberty?",
                        "When should I be concerned about delayed puberty?", 
                        "How do growth spurts affect different body parts?"
                    ],
                    "Related Topics": [
                        "How to maintain good hygiene during puberty?",
                        "What role do hormones play in development?",
                        "How to deal with body image concerns?"
                    ],
                    "Family & Culture": [
                        "How do I talk to my parents about body changes?",
                        "How do cultural attitudes affect puberty discussions?",
                        "What should I know about privacy and boundaries?"
                    ]
                }
            elif any(word in user_lower for word in ["body", "anatomy", "reproductive"]):
                return {
                    "Understanding Basics": [
                        "What's the difference between biological sex and gender?",
                        "How do hormones affect mood and behavior?",
                        "What are common myths about human anatomy?"
                    ],
                    "Health & Wellness": [
                        "How to maintain reproductive health?",
                        "When should I see a doctor about body concerns?",
                        "What are normal vs concerning symptoms?"
                    ],
                    "Education Resources": [
                        "Where can I find reliable health information?",
                        "How to ask healthcare providers questions?",
                        "What books or resources are recommended?"
                    ]
                }
            else:
                return {
                    "Getting Started": [
                        "What physical changes happen first during puberty?",
                        "How do I talk to my parents about body changes?",
                        "Why do people develop at different rates?"
                    ],
                    "Practical Guidance": [
                        "How to prepare for physical changes?",
                        "What products or supplies might I need?",
                        "How to build body confidence?"
                    ]
                }
        
        elif current_intent == "relationship_guidance":
            if any(word in user_lower for word in ["ready", "first", "start"]):
                return {
                    "Self-Assessment": [
                        "What are red flags to watch for in relationships?",
                        "How do you know if someone genuinely likes you?",
                        "What's the difference between crush and love?"
                    ],
                    "Building Foundations": [
                        "How to build self-confidence before dating?",
                        "What are healthy relationship expectations?",
                        "How to communicate your boundaries clearly?"
                    ],
                    "Cultural Considerations": [
                        "How do family expectations affect relationships?",
                        "Navigating traditional vs modern relationship views",
                        "How to respect cultural differences in relationships?"
                    ]
                }
            elif any(word in user_lower for word in ["communication", "talk", "express"]):
                return {
                    "Communication Skills": [
                        "How do you handle disagreements in relationships?",
                        "What if my partner and I have different communication styles?",
                        "How to express needs without being demanding?"
                    ],
                    "Conflict Resolution": [
                        "How to apologize effectively in relationships?",
                        "When to seek help for relationship problems?",
                        "How to know when a relationship isn't working?"
                    ],
                    "Cultural Dynamics": [
                        "How do cultural differences affect relationships?",
                        "Navigating language barriers in relationships",
                        "How to involve families in relationship decisions?"
                    ]
                }
            else:
                return {
                    "Relationship Health": [
                        "What makes relationships healthy vs unhealthy?",
                        "How do you maintain friendships while in a relationship?",
                        "What role should family play in relationship decisions?"
                    ],
                    "Personal Growth": [
                        "How to maintain your identity in a relationship?",
                        "Balancing personal goals with relationship goals",
                        "How to grow together as a couple?"
                    ]
                }
        
        elif current_intent == "health_safety":
            if any(word in user_lower for word in ["protect", "safe", "prevention"]):
                return {
                    "Protection Methods": [
                        "What are the most effective forms of protection?",
                        "How do different protection methods work?",
                        "Where to access protection and contraceptives?"
                    ],
                    "Communication": [
                        "How do you discuss safety with a partner?",
                        "How to bring up protection in conversations?",
                        "What if a partner refuses to use protection?"
                    ],
                    "Emergency Situations": [
                        "What should I do if protection fails?",
                        "Emergency contraception: what to know?",
                        "When to seek immediate medical help?"
                    ]
                }
            elif any(word in user_lower for word in ["sti", "std", "infection"]):
                return {
                    "Testing & Prevention": [
                        "How often should someone get tested?",
                        "What are the symptoms I should watch for?",
                        "How to prevent STI transmission?"
                    ],
                    "Communication": [
                        "How do you tell a partner about STI status?",
                        "How to ask a partner about their testing history?",
                        "Dealing with STI stigma and shame"
                    ],
                    "Treatment & Support": [
                        "What happens if I test positive for an STI?",
                        "How to find confidential testing services?",
                        "Support resources for those with STIs"
                    ]
                }
            else:
                return {
                    "Health Communication": [
                        "What health topics should couples discuss?",
                        "How to ask healthcare providers sensitive questions?",
                        "When should someone see a doctor?"
                    ],
                    "Reliable Information": [
                        "How do you find trustworthy health information?",
                        "Identifying myths vs medical facts",
                        "Best health resources for young adults"
                    ]
                }
        
        elif current_intent == "consent_education":
            if any(word in user_lower for word in ["consent", "permission", "agreement"]):
                return {
                    "Understanding Consent": [
                        "How do you give enthusiastic consent?",
                        "What's the difference between consent and compliance?",
                        "How do alcohol and drugs affect consent?"
                    ],
                    "Consent in Practice": [
                        "What if someone changes their mind during intimacy?",
                        "How to check for ongoing consent?",
                        "Non-verbal signs of consent and discomfort"
                    ],
                    "Legal & Cultural Aspects": [
                        "How do cultural attitudes affect consent?",
                        "Legal aspects of consent in India",
                        "Age of consent and what it means"
                    ]
                }
            elif any(word in user_lower for word in ["boundaries", "limits", "comfort"]):
                return {
                    "Setting Boundaries": [
                        "How do you communicate boundaries clearly?",
                        "How to identify your own boundaries?",
                        "Setting boundaries in different relationships"
                    ],
                    "Respecting Boundaries": [
                        "How do you respect someone's boundaries?",
                        "What if your boundaries are different from your partner's?",
                        "How to respond when boundaries are shared"
                    ],
                    "When Boundaries Are Crossed": [
                        "What should you do if boundaries are crossed?",
                        "How to address boundary violations?",
                        "Support resources for boundary violations"
                    ]
                }
            else:
                return {
                    "Consent Basics": [
                        "What's the difference between consent and compliance?",
                        "How do cultural attitudes affect consent?",
                        "Understanding different types of consent"
                    ],
                    "Communication Skills": [
                        "How to have conversations about consent?",
                        "Teaching consent to others",
                        "Consent in digital communication"
                    ]
                }
        
        elif current_intent == "cultural_context":
            return {
                "Navigating Differences": [
                    "How do you navigate conflicting cultural values?",
                    "What if your family has different expectations?",
                    "How do you respect culture while making personal choices?"
                ],
                "Family Dynamics": [
                    "How to have difficult conversations with traditional parents?",
                    "Balancing independence with family respect",
                    "When family values conflict with personal beliefs"
                ],
                "Modern vs Traditional": [
                    "How to bridge generational gaps in thinking?",
                    "Adapting cultural traditions to modern context",
                    "Finding support when culture feels restrictive"
                ]
            }
        
        else:  # general_inquiry
            return {
                "Explore Topics": [
                    "What topics are you most curious about?",
                    "Is there something specific you'd like to understand better?",
                    "What would be most helpful for you to learn right now?"
                ],
                "Getting Started": [
                    "How to start learning about sexual health?",
                    "Common questions people your age ask",
                    "Building confidence to ask questions"
                ],
                "Resources & Support": [
                    "Where to find reliable health information?",
                    "How to talk to trusted adults about these topics?",
                    "Support groups and communities for learning"
                ]
            }


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
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 2  # seconds
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
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
        
        # Get mode-specific instructions
        mode_instruction = self.memory.get_mode_instruction()
        
        # Add citation requirements for all responses
        citation_instruction = "\n\nIMPORTANT: Always include relevant sources and citations in your response. When providing medical, health, or educational information, cite authoritative sources like WHO, medical journals, government health departments, or established educational institutions. Format citations as [Source: Organization/Website name]."
        
        task_descriptions = {
            "crisis": f"""
                URGENT: The user may be in distress. Analyze this message: "{user_input}"
                
                Context: {context}
                
                Provide immediate supportive response and escalation guidance if needed.
                Include relevant helpline numbers for India.{mode_instruction}{citation_instruction}
                """,
            
            "anatomy_education": f"""
                Provide age-appropriate, medically accurate information about: "{user_input}"
                
                Context: {context}
                
                Ensure content is culturally sensitive for Indian context and scientifically accurate.{mode_instruction}{citation_instruction}
                """,
            
            "relationship_guidance": f"""
                Provide guidance on healthy relationships regarding: "{user_input}"
                
                Context: {context}
                
                Focus on respect, communication, and cultural sensitivity in Indian context.{mode_instruction}{citation_instruction}
                """,
            
            "health_safety": f"""
                Provide health and safety information about: "{user_input}"
                
                Context: {context}
                
                Include medically accurate information and emphasize consulting healthcare providers.{mode_instruction}{citation_instruction}
                """,
            
            "consent_education": f"""
                Educate about consent and boundaries regarding: "{user_input}"
                
                Context: {context}
                
                Emphasize respect, communication, and legal aspects in Indian context.{mode_instruction}{citation_instruction}
                """,
            
            "cultural_context": f"""
                Address cultural aspects of: "{user_input}"
                
                Context: {context}
                
                Balance traditional values with comprehensive sex education principles.{mode_instruction}{citation_instruction}
                """,
            
            "general_inquiry": f"""
                Respond to this general sex education query: "{user_input}"
                
                Context: {context}
                
                Provide helpful, age-appropriate, and culturally sensitive information.{mode_instruction}{citation_instruction}
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
    
    def _execute_with_retry(self, mini_crew: Crew, user_input: str, intent: str) -> Optional[str]:
        """Execute crew task with automatic retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{self.max_retries} for intent: {intent}")
                
                # Execute the task
                result = mini_crew.kickoff()
                
                # Extract response text
                response = str(result)
                
                self.logger.info(f"Successfully got response on attempt {attempt + 1}")
                return response
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if this is a retryable error
                if self._is_retryable_error(error_str):
                    self.logger.warning(f"Attempt {attempt + 1} failed with retryable error: {e}")
                    
                    if attempt < self.max_retries - 1:
                        # Calculate delay with exponential backoff
                        delay = self.base_delay * (2 ** attempt)
                        self.logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        self.logger.error(f"All {self.max_retries} attempts failed for intent '{intent}'")
                        raise e
                else:
                    # Non-retryable error, don't retry
                    self.logger.error(f"Non-retryable error for intent '{intent}': {e}")
                    raise e
        
        return None
    
    def _is_retryable_error(self, error_str: str) -> bool:
        """Check if an error is worth retrying"""
        retryable_indicators = [
            'overloaded', '503', 'unavailable', 'timeout', 
            'connection', 'network', 'temporary', 'busy'
        ]
        return any(indicator in error_str for indicator in retryable_indicators)
    
    def process_user_input(self, user_input: str, mode: str = None) -> Dict:
        """Main method to process user input and generate structured response"""
        
        # Set mode if provided
        if mode:
            try:
                self.memory.set_explanation_mode(mode)
            except ValueError as e:
                return {
                    "response": f"Invalid mode: {str(e)}",
                    "suggestions": ["Tell me about relationships", "How do I stay safe?", "What is consent?"],
                    "intent": "error"
                }
        
        # Add user message to memory
        self.memory.add_message("user", user_input)
        
        # Check appropriateness
        is_appropriate, inappropriate_msg = self.check_appropriateness(user_input)
        if not is_appropriate:
            self.memory.add_message("assistant", inappropriate_msg)
            return {
                "response": inappropriate_msg,
                "suggestions": ["I want to learn about healthy relationships", "Tell me about body changes", "How do I stay safe?"],
                "intent": "inappropriate",
                "current_mode": self.memory.get_current_mode(),
                "mode_info": self.memory.get_mode_info()
            }
        
        # Detect intent
        intent = self.detect_intent(user_input)
        
        # Track discussed topic
        self.memory.add_discussed_topic(intent)
        
        # Get conversation context
        context = self.memory.get_context()
        
        # Handle crisis situations
        if intent == "crisis":
            crisis_response = self._handle_crisis_response(user_input)
            self.memory.add_message("assistant", crisis_response, {"intent": intent})
            return {
                "response": crisis_response,
                "suggestions": ["I want to talk about something else", "Tell me about support resources", "Help me find professional help"],
                "intent": intent,
                "current_mode": self.memory.get_current_mode(),
                "mode_info": self.memory.get_mode_info()
            }
        
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
            
            # Execute the task with retry logic
            response = self._execute_with_retry(mini_crew, user_input, intent)
            
            if response is None:
                raise Exception("Failed to get response after all retries")
            
            # Get follow-up suggestions (convert to simple list for now due to API issues)
            suggestions_raw = self.memory.get_follow_up_suggestions(intent, user_input)
            
            # Convert categorized suggestions to simple list for stability
            if isinstance(suggestions_raw, dict):
                suggestions = []
                for category_suggestions in suggestions_raw.values():
                    suggestions.extend(category_suggestions[:2])  # Take 2 from each category
                suggestions = suggestions[:6]  # Limit total
            else:
                suggestions = suggestions_raw
            
            # Add response to memory
            self.memory.add_message("assistant", response, {"intent": intent})
            
            return {
                "response": response,
                "suggestions": suggestions,
                "intent": intent,
                "current_mode": self.memory.get_current_mode(),
                "mode_info": self.memory.get_mode_info()
            }
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Provide specific error messages for common issues
            if 'overloaded' in error_str or '503' in error_str:
                error_response = "I'm experiencing high demand right now. Please try asking your question again in a moment, or rephrase it for better results."
            elif 'timeout' in error_str or 'unavailable' in error_str:
                error_response = "I'm temporarily having connectivity issues. Please try again shortly."
            else:
                error_response = "I apologize, but I'm having trouble processing your question right now. Could you please rephrase it or try asking something else?"
            
            # Log the error for debugging
            import logging
            logging.error(f"Chatbot error for intent '{intent}': {e}")
            
            self.memory.add_message("assistant", error_response, {"error": str(e)})
            return {
                "response": error_response,
                "suggestions": ["I want to learn about relationships", "Tell me about body changes", "How do I stay healthy?"],
                "intent": "error",
                "current_mode": self.memory.get_current_mode(),
                "mode_info": self.memory.get_mode_info()
            }
    
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