import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ClaudeLLM:
    """
    Integrates with Anthropic's Claude API
    Handles prompt construction, API calls, and error handling
    """
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "claude-3-5-sonnet-20241022",
                 temperature: float = 0.2,
                 max_tokens: int = 1000):
        """
        Initialize Claude LLM
        
        Args:
            api_key: Anthropic API key (from env if not provided)
            model: Model name
            temperature: Temperature for response (0-1, lower = more deterministic)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment")
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info(f"Claude LLM initialized with model: {model}")
        except ImportError:
            logger.error("anthropic package not installed. Install with: pip install anthropic")
            raise
        except Exception as e:
            logger.error(f"Error initializing Claude client: {str(e)}")
            raise
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate response using Claude
        
        Args:
            prompt: Input prompt
            
        Returns:
            Dictionary with generated text and token usage
        """
        try:
            if not prompt or not isinstance(prompt, str):
                logger.error("Invalid prompt")
                return {
                    "text": "Error: Invalid prompt provided",
                    "tokens_used": 0,
                    "error": "Invalid prompt"
                }
            
            logger.info(f"Calling Claude API with model: {self.model}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract response
            response_text = message.content[0].text
            tokens_used = message.usage.output_tokens
            
            logger.info(f"Claude response generated. Tokens used: {tokens_used}")
            
            return {
                "text": response_text,
                "tokens_used": tokens_used,
                "model": self.model,
                "input_tokens": message.usage.input_tokens
            }
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}", exc_info=True)
            
            # Return error response
            return {
                "text": f"I encountered an error processing your request: {str(e)}",
                "tokens_used": None,
                "error": str(e),
                "model": self.model
            }
    
    def generate_with_system_prompt(self,
                                   system_prompt: str,
                                   user_prompt: str) -> Dict[str, Any]:
        """
        Generate with explicit system prompt
        
        Args:
            system_prompt: System instruction
            user_prompt: User message
            
        Returns:
            Dictionary with response and metrics
        """
        try:
            logger.info("Calling Claude with system prompt")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            tokens_used = message.usage.output_tokens
            
            return {
                "text": response_text,
                "tokens_used": tokens_used,
                "input_tokens": message.usage.input_tokens
            }
            
        except Exception as e:
            logger.error(f"Error with system prompt: {str(e)}")
            return {
                "text": f"Error: {str(e)}",
                "tokens_used": None,
                "error": str(e)
            }
    
    def validate_api_key(self) -> bool:
        """
        Validate API key by making a simple request
        
        Returns:
            True if valid, False otherwise
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Say ok"
                    }
                ]
            )
            logger.info("API key validation successful")
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about current model configuration"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
