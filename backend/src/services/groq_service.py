"""
Groq AI service for generating language learning content.
"""

import os
import logging
from typing import Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GroqService:
    """Service for interacting with Groq AI API."""

    def __init__(self):
        """Initialize Groq client with API key from environment."""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if Groq service is available."""
        return self.client is not None and self.api_key is not None

    async def test_connection(self) -> Dict[str, Any]:
        """Test Groq API connection with a simple completion."""
        if not self.is_available():
            return {
                "error": "groq_unavailable",
                "message": "Groq API key not configured or client initialization failed",
            }

        try:
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, respond with 'OK' if you can hear me.",
                    }
                ],
                temperature=0.1,
                max_tokens=10,
            )

            content = completion.choices[0].message.content.strip()
            tokens_used = (
                completion.usage.total_tokens if completion.usage else 0
            )

            return {
                "content": content,
                "model": "openai/gpt-oss-20b",
                "tokens_used": tokens_used,
            }

        except Exception as e:
            logger.error(f"Groq API test failed: {e}")
            return {
                "error": "groq_api_error",
                "message": f"Failed to connect to Groq API: {str(e)}",
            }

    async def generate_completion(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a completion using Groq AI with a simple prompt.

        Args:
            prompt: The prompt to send to the AI

        Returns:
            Dict with content, model, tokens_used or error information
        """
        if not self.is_available():
            return {
                "error": "groq_unavailable",
                "message": "Groq API key not configured or client initialization failed",
            }

        try:
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
            )

            content = completion.choices[0].message.content.strip()
            tokens_used = (
                completion.usage.total_tokens if completion.usage else 0
            )

            return {
                "content": content,
                "model": "openai/gpt-oss-20b",
                "tokens_used": tokens_used,
            }

        except Exception as e:
            logger.error(f"Groq completion generation failed: {e}")
            return {
                "error": "groq_generation_error",
                "message": f"Failed to generate completion: {str(e)}",
            }

    async def generate_practice_content(
        self,
        korean_word: str,
        english_translation: str,
        practice_type: str = "definition",
    ) -> Dict[str, Any]:
        """
        Generate practice content for a Korean word using Groq AI.

        Args:
            korean_word: The Korean word
            english_translation: English translation
            practice_type: Type of practice content ("definition", "example", "quiz")

        Returns:
            Dict with content, model, tokens_used or error information
        """
        if not self.is_available():
            return {
                "error": "groq_unavailable",
                "message": "Groq API key not configured or client initialization failed",
            }

        # Create appropriate prompt based on practice type
        prompts = {
            "definition": f"""You are a Korean language tutor. Create a helpful explanation for the Korean word "{korean_word}" which means "{english_translation}". 
            
Provide:
1. A clear definition
2. Any relevant grammar notes
3. Common usage context

Keep it concise and educational. Respond in English.""",
            "example": f"""You are a Korean language tutor. Create 2-3 example sentences using the Korean word "{korean_word}" (meaning: {english_translation}).

For each example:
1. Write the Korean sentence
2. Provide the English translation
3. Highlight how the word is used

Format as a simple list. Keep it practical and useful for learners.""",
            "quiz": f"""You are a Korean language tutor. Create a simple quiz question about the Korean word "{korean_word}" (meaning: {english_translation}).

Create either:
1. A multiple choice question with 4 options
2. A fill-in-the-blank sentence
3. A translation challenge

Make it appropriate for intermediate learners. Include the correct answer.""",
        }

        prompt = prompts.get(practice_type, prompts["definition"])

        try:
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful Korean language tutor focused on clear, educational content.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )

            content = completion.choices[0].message.content.strip()
            tokens_used = (
                completion.usage.total_tokens if completion.usage else 0
            )

            return {
                "content": content,
                "model": "openai/gpt-oss-20b",
                "tokens_used": tokens_used,
            }

        except Exception as e:
            logger.error(f"Groq content generation failed: {e}")
            return {
                "error": "groq_generation_error",
                "message": f"Failed to generate content: {str(e)}",
            }


# Global instance
groq_service = GroqService()
