#!/usr/bin/env python3
"""
Agentic quiz generation tool using Groq API.
Generates hints and distractors for quiz items while keeping answers deterministic.
"""
from typing import List, Dict, Any, Optional
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QuizItem:
    """Represents a quiz item with Korean word, English answer, hint, and distractors"""

    word_id: int
    korean: str
    answer_en: str
    hint: Optional[str] = None
    distractors: Optional[List[str]] = None


class AgentQuizGenerator:
    """
    Generates quiz items with AI-powered hints and distractors using Groq.
    """

    def __init__(self, groq_service):
        self.groq_service = groq_service

    async def generate_quiz_items(
        self, base_words: List[Dict[str, Any]], level: str = "TOPIK1"
    ) -> List[QuizItem]:
        """
        Generate quiz items with hints and distractors for the given words.

        Args:
            base_words: List of word dicts with keys: id, korean, english
            level: Difficulty level (TOPIK1, TOPIK2, etc.)

        Returns:
            List of QuizItem objects with generated hints and distractors
        """
        if not base_words:
            return []

        try:
            # Create the prompt for Groq
            prompt = self._create_quiz_prompt(base_words, level)

            # Call Groq API
            response = await self.groq_service.generate_completion(prompt)

            if "error" in response:
                logger.error(f"Groq API error: {response}")
                # Return basic items without AI enhancement
                return self._create_basic_items(base_words)

            # Parse the AI response
            enhanced_items = self._parse_groq_response(
                response["content"], base_words
            )

            return enhanced_items

        except Exception as e:
            logger.error(f"Error generating quiz items: {e}")
            # Fallback to basic items
            return self._create_basic_items(base_words)

    def _create_quiz_prompt(
        self, words: List[Dict[str, Any]], level: str
    ) -> str:
        """Create a prompt for Groq to generate hints and distractors."""

        words_list = "\n".join(
            [
                f"{i+1}. {word['korean']} → {word['english']}"
                for i, word in enumerate(words)
            ]
        )

        prompt = f"""You are a Korean language teacher creating quiz questions for {level} level students.

For each Korean word below, provide:
1. A helpful hint in English (not the direct translation)
2. Three plausible but incorrect English distractors

Words to enhance:
{words_list}

Please respond in this exact JSON format:
{{
  "items": [
    {{
      "korean": "word1",
      "hint": "A helpful hint about the word's meaning or usage",
      "distractors": ["wrong1", "wrong2", "wrong3"]
    }},
    {{
      "korean": "word2", 
      "hint": "Another helpful hint",
      "distractors": ["wrong1", "wrong2", "wrong3"]
    }}
  ]
}}

Guidelines:
- Hints should help students understand the word without giving away the answer
- Distractors should be plausible wrong answers in English
- Keep hints concise (1-2 sentences max)
- Make distractors similar in length/style to the correct answer
- Ensure all content is appropriate for language learners"""

        return prompt

    def _parse_groq_response(
        self, content: str, base_words: List[Dict[str, Any]]
    ) -> List[QuizItem]:
        """Parse Groq's JSON response and create QuizItem objects."""
        try:
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)
            items = []

            # Create a lookup for base words by Korean text
            word_lookup = {word["korean"]: word for word in base_words}

            for item_data in data.get("items", []):
                korean = item_data.get("korean", "")
                if korean in word_lookup:
                    base_word = word_lookup[korean]

                    quiz_item = QuizItem(
                        word_id=base_word["id"],
                        korean=korean,
                        answer_en=base_word["english"],
                        hint=item_data.get("hint"),
                        distractors=item_data.get("distractors", []),
                    )
                    items.append(quiz_item)

            # If we didn't get all items, fill in the missing ones
            if len(items) < len(base_words):
                enhanced_korean = {item.korean for item in items}
                for word in base_words:
                    if word["korean"] not in enhanced_korean:
                        items.append(
                            QuizItem(
                                word_id=word["id"],
                                korean=word["korean"],
                                answer_en=word["english"],
                                hint=None,
                                distractors=None,
                            )
                        )

            return items

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Groq response: {e}")
            logger.error(f"Response content: {content}")
            return self._create_basic_items(base_words)

    def _create_basic_items(
        self, base_words: List[Dict[str, Any]]
    ) -> List[QuizItem]:
        """Create basic quiz items without AI enhancement (fallback)."""
        return [
            QuizItem(
                word_id=word["id"],
                korean=word["korean"],
                answer_en=word["english"],
                hint=None,
                distractors=None,
            )
            for word in base_words
        ]


def generate_quiz_items_from_dict(
    words_data: List[Dict[str, Any]], level: str = "TOPIK1", groq_service=None
) -> List[Dict[str, Any]]:
    """
    Generate quiz items from dictionary data (for API usage).

    Args:
        words_data: List of word dicts with keys: id, korean, english
        level: Difficulty level
        groq_service: Groq service instance

    Returns:
        List of dictionaries with quiz item data
    """
    if not groq_service:
        # Return basic items without enhancement
        return [
            {
                "word_id": word["id"],
                "korean": word["korean"],
                "answer_en": word["english"],
                "hint": None,
                "distractors": None,
            }
            for word in words_data
        ]

    # This would be called asynchronously in the actual API
    # For now, return basic items as this is a sync function
    return [
        {
            "word_id": word["id"],
            "korean": word["korean"],
            "answer_en": word["english"],
            "hint": None,
            "distractors": None,
        }
        for word in words_data
    ]


# Example usage and testing
if __name__ == "__main__":
    # Test data
    test_words = [
        {"id": 1, "korean": "안녕하세요", "english": "hello"},
        {"id": 2, "korean": "감사합니다", "english": "thank you"},
        {"id": 3, "korean": "죄송합니다", "english": "sorry"},
    ]

    print("Agent Quiz Generator Test:")
    print("=" * 40)

    # Test basic item creation (without Groq)
    basic_items = generate_quiz_items_from_dict(test_words)

    print("Basic items (no AI enhancement):")
    for item in basic_items:
        print(f"  {item['korean']} → {item['answer_en']}")
        print(f"    Hint: {item['hint']}")
        print(f"    Distractors: {item['distractors']}")

    print(
        "\nNote: Full AI enhancement requires async Groq service integration"
    )
