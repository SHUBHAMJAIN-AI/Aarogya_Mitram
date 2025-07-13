#!/usr/bin/env python
"""
LLM Utility Functions for Resilient API Calls
Handles retries, fallbacks, and error recovery
"""

import os
import time
import logging
from typing import Optional, Any
from crewai import LLM

logger = logging.getLogger(__name__)

class ResilientLLM:
    """Wrapper for LLM calls with retry logic and fallback models"""
    
    def __init__(self):
        self.primary_model = os.getenv('MODEL', 'gemini/gemini-1.5-flash')
        self.fallback_model = os.getenv('FALLBACK_MODEL')
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '2'))
        
        # Initialize primary LLM
        self.primary_llm = LLM(model=self.primary_model)
        
        # Initialize fallback LLM if available
        self.fallback_llm = None
        if self.fallback_model:
            try:
                self.fallback_llm = LLM(model=self.fallback_model)
                logger.info(f"Fallback LLM initialized: {self.fallback_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize fallback LLM: {e}")
    
    def get_llm(self, use_fallback: bool = False) -> LLM:
        """Get appropriate LLM instance"""
        if use_fallback and self.fallback_llm:
            logger.info("Using fallback LLM")
            return self.fallback_llm
        return self.primary_llm
    
    def call_with_retry(self, prompt: str, use_fallback: bool = False) -> Optional[str]:
        """
        Make LLM call with retry logic
        
        Args:
            prompt: The prompt to send
            use_fallback: Whether to use fallback model
            
        Returns:
            Response string or None if all attempts fail
        """
        llm = self.get_llm(use_fallback)
        
        for attempt in range(self.max_retries):
            try:
                response = llm.call(prompt)
                return response
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for specific overload errors
                if 'overloaded' in error_msg or '503' in error_msg or 'unavailable' in error_msg:
                    logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed - Model overloaded: {e}")
                    
                    if attempt < self.max_retries - 1:
                        # Wait before retry
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Try fallback if available and not already using it
                        if not use_fallback and self.fallback_llm:
                            logger.info("Primary model failed, trying fallback model...")
                            return self.call_with_retry(prompt, use_fallback=True)
                        
                else:
                    # For non-overload errors, don't retry
                    logger.error(f"LLM call failed with non-retryable error: {e}")
                    break
        
        logger.error(f"All LLM call attempts failed")
        return None

# Global instance
resilient_llm = ResilientLLM()

def get_resilient_llm() -> LLM:
    """Get the primary LLM with resilience features"""
    return resilient_llm.primary_llm

def make_resilient_call(prompt: str) -> Optional[str]:
    """Make a resilient LLM call with retries and fallback"""
    return resilient_llm.call_with_retry(prompt)