"""Script Generator Service using Google Gemini 2.0 Flash.

This service generates engaging 60-90 second scripts from lesson content
using Google Gemini 2.0 Flash API.

Script Structure:
1. Hook (0-5 seconds) - Attention-grabbing opening
2. Core Concept (5-30 seconds) - Main teaching point
3. Example/Proof (30-50 seconds) - Concrete example or code
4. Call-to-Action (50-60 seconds) - Direct to full lesson

Target Cost: ~$0.002 per script
"""

import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from google import genai

from shorts_generator.core.config import settings
from shorts_generator.services.content_extractor import LessonContent

logger = logging.getLogger(__name__)

# Average speaking rate: 150 words per minute = 2.5 words per second
WORDS_PER_SECOND = 2.5


@dataclass
class ScriptScene:
    """Represents a single scene in the script.

    Attributes:
        text: Spoken narration text
        visual_description: Description for AI image generation
        duration_seconds: Target duration in seconds
        scene_type: Type of scene (hook, concept, example, cta)
    """

    text: str
    visual_description: str
    duration_seconds: int
    scene_type: str = "concept"


@dataclass
class GeneratedScript:
    """Represents a complete generated script.

    Attributes:
        lesson_path: Source lesson path
        lesson_title: Title of the source lesson
        hook: Opening hook scene
        concepts: List of concept scenes
        example: Example/proof scene
        cta: Call-to-action scene
        total_duration: Total target duration in seconds
        visual_descriptions: JSON object with all visual descriptions
        created_at: When the script was generated
        model_used: Which model generated this script
    """

    lesson_path: str
    lesson_title: str
    hook: ScriptScene
    concepts: list[ScriptScene]
    example: ScriptScene
    cta: ScriptScene
    total_duration: int
    visual_descriptions: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    model_used: str = "gemini-2.0-flash-exp"


class ScriptGenerator:
    """Generates short video scripts using Google Gemini 2.0 Flash."""

    def __init__(self):
        """Initialize the script generator with the new Google GenAI client."""
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def _calculate_word_count(self, duration_seconds: int) -> int:
        """Calculate target word count for a duration.

        Args:
            duration_seconds: Target duration in seconds

        Returns:
            Target word count
        """
        return int(duration_seconds * WORDS_PER_SECOND)

    def _estimate_duration(self, word_count: int) -> int:
        """Estimate spoken duration from word count.

        Args:
            word_count: Number of words

        Returns:
            Estimated duration in seconds
        """
        return max(5, int(word_count / WORDS_PER_SECOND))

    def _build_generation_prompt(
        self,
        lesson: LessonContent,
        target_duration: int = 60,
    ) -> str:
        """Build the prompt for script generation.

        Args:
            lesson: Parsed lesson content
            target_duration: Target duration in seconds

        Returns:
            Prompt string for Gemini
        """
        # Calculate word budget
        hook_words = self._calculate_word_count(5)  # 5 seconds
        concept_words = self._calculate_word_count(25)  # 25 seconds
        example_words = self._calculate_word_count(20)  # 20 seconds
        cta_words = self._calculate_word_count(10)  # 10 seconds

        # Build concepts summary
        concepts_summary = "\n".join(
            [f"- {c.title}: {c.content[:100]}..." for c in lesson.concepts[:3]]
        )

        # Build code examples summary
        code_summary = ""
        if lesson.code_blocks:
            code_summary = f"\nCode examples available in: {', '.join(set(cb.language for cb in lesson.code_blocks[:3]))}"

        prompt = f"""You are an expert educational content creator specializing in short-form videos (60-90 seconds) for platforms like YouTube Shorts, TikTok, and Instagram Reels.

Generate an engaging script for a short video from this lesson:

**Lesson**: {lesson.title}
**Difficulty**: {lesson.difficulty_level}
**Duration**: {target_duration} seconds

**Key Concepts**:
{concepts_summary}
{code_summary}

**Script Requirements**:
1. Hook ({hook_words} words): MUST start with a surprising question, statistic, or bold statement that grabs attention immediately
2. Core Concept ({concept_words} words): Explain ONE key idea clearly and simply
3. Example ({example_words} words): Concrete proof, code snippet, or real-world application
4. Call-to-Action ({cta_words} words): Direct viewers to read the full lesson

**Visual Style**:
- Modern, tech-focused with AI aesthetic
- Clean typography and smooth animations
- Use bold colors (purple/blue gradient) matching brand

**Tone**: Energetic, educational, accessible - not jargon-heavy

**IMPORTANT**: Respond with ONLY the raw JSON object. No markdown formatting, no code blocks, no explanations. Just the JSON.

**Output Format**:
{{
  "hook": {{"text": "Hook text", "visual": "Visual description for AI image generator", "duration": 5}},
  "concepts": [
    {{"text": "Concept explanation", "visual": "Visual description", "duration": 15}},
    {{"text": "Additional detail", "visual": "Visual description", "duration": 10}}
  ],
  "example": {{"text": "Example with proof/code", "visual": "Screenshot or diagram description", "duration": 20}},
  "cta": {{"text": "Call to action text", "visual": "Lesson cover with link", "duration": 10}}
}}

**Constraints**:
- Total duration must be approximately {target_duration} seconds
- Each section's duration must sum correctly
- Hook MUST be provocative (e.g., "Did you know...", "Here's why...", "The truth about...")
- CTA must include: "Read the full lesson at [link]"
- Visual descriptions should be specific enough for AI image generation (e.g., "Futuristic AI brain network with glowing purple and blue neural connections on dark background")

Respond with ONLY the JSON object, nothing else:"""

        return prompt

    async def generate_script(
        self,
        lesson: LessonContent,
        target_duration: int = 60,
    ) -> GeneratedScript:
        """Generate a script from lesson content.

        Args:
            lesson: Parsed lesson content
            target_duration: Target duration in seconds (default: 60)

        Returns:
            GeneratedScript object with all scenes

        Raises:
            Exception: If generation fails
        """
        logger.info(f"Generating script for: {lesson.lesson_path}")

        # Build prompt
        prompt = self._build_generation_prompt(lesson, target_duration)

        try:
            # Generate content using new Google GenAI SDK
            # The new SDK uses synchronous calls - run in thread pool for async
            import asyncio

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=prompt,
                config={
                    "temperature": 0.7,
                    "max_output_tokens": 2000,  # Increased from 500 to avoid truncation
                    "response_mime_type": "application/json",
                },
            )

            # Get response text
            response_text = response.text
            logger.info(f"Gemini response length: {len(response_text)}")
            logger.debug(f"Gemini response preview: {response_text[:200]}...")

            # Extract JSON from response (handle markdown code blocks)
            json_text = response_text.strip()

            # Remove markdown code blocks if present
            if json_text.startswith("```"):
                # Extract content between ```json and ``` or just ``` and ```
                lines = json_text.split("\n")
                if lines[0].startswith("```json"):
                    lines = lines[1:]  # Remove opening ```json
                elif lines[0].startswith("```"):
                    lines = lines[1:]  # Remove opening ```

                # Find closing ```
                for i, line in enumerate(lines):
                    if line.strip() == "```":
                        lines = lines[:i]
                        break

                json_text = "\n".join(lines).strip()

            logger.debug(f"Extracted JSON preview: {json_text[:200]}...")

            # Parse response
            script_data = json.loads(json_text)

            # Validate structure
            if not all(key in script_data for key in ["hook", "concepts", "example", "cta"]):
                raise ValueError("Invalid script structure from Gemini")

            # Create script objects
            hook = ScriptScene(
                text=script_data["hook"]["text"],
                visual_description=script_data["hook"]["visual"],
                duration_seconds=script_data["hook"]["duration"],
                scene_type="hook",
            )

            concepts = [
                ScriptScene(
                    text=c["text"],
                    visual_description=c["visual"],
                    duration_seconds=c["duration"],
                    scene_type="concept",
                )
                for c in script_data["concepts"]
            ]

            example = ScriptScene(
                text=script_data["example"]["text"],
                visual_description=script_data["example"]["visual"],
                duration_seconds=script_data["example"]["duration"],
                scene_type="example",
            )

            cta = ScriptScene(
                text=script_data["cta"]["text"],
                visual_description=script_data["cta"]["visual"],
                duration_seconds=script_data["cta"]["duration"],
                scene_type="cta",
            )

            # Calculate total duration
            total_duration = (
                hook.duration_seconds
                + sum(c.duration_seconds for c in concepts)
                + example.duration_seconds
                + cta.duration_seconds
            )

            # Build visual descriptions JSON
            visual_descriptions = {
                "hook": script_data["hook"]["visual"],
                "concepts": [c["visual"] for c in script_data["concepts"]],
                "example": script_data["example"]["visual"],
                "cta": script_data["cta"]["visual"],
            }

            generated_script = GeneratedScript(
                lesson_path=lesson.lesson_path,
                lesson_title=lesson.title,
                hook=hook,
                concepts=concepts,
                example=example,
                cta=cta,
                total_duration=total_duration,
                visual_descriptions=visual_descriptions,
                model_used=settings.gemini_model,
            )

            logger.info(f"Script generated successfully: {total_duration}s target duration")

            return generated_script

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}") from e
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise

    def validate_timing(self, script: GeneratedScript, tolerance_seconds: int = 10) -> bool:
        """Validate that script timing is within acceptable range.

        Args:
            script: Generated script to validate
            tolerance_seconds: Acceptable deviation from target

        Returns:
            True if timing is valid, False otherwise
        """
        target_duration = 60  # Default target
        deviation = abs(script.total_duration - target_duration)

        return deviation <= tolerance_seconds

    def format_for_tts(self, script: GeneratedScript) -> str:
        """Format script for text-to-speech generation.

        Combines all scenes into a single text with pause indicators.

        Args:
            script: Generated script

        Returns:
            Formatted text for TTS
        """
        parts = []

        # Hook
        parts.append(f"{script.hook.text}")

        # Concepts
        for concept in script.concepts:
            parts.append(f"{concept.text}")

        # Example
        parts.append(f"{script.example.text}")

        # CTA
        parts.append(f"{script.cta.text}")

        return " ".join(parts)

    def get_script_text(self, script: GeneratedScript) -> str:
        """Get the full script as formatted text.

        Args:
            script: Generated script

        Returns:
            Formatted script text with scene markers
        """
        lines = [
            f"# {script.lesson_title}",
            "",
            f"**Duration**: {script.total_duration}s",
            f"**Model**: {script.model_used}",
            "",
            "## Hook",
            f"{script.hook.text}",
            f"[Visual: {script.hook.visual_description}]",
            "",
            "## Concepts",
        ]

        for i, concept in enumerate(script.concepts, 1):
            lines.append(f"{i}. {concept.text}")
            lines.append(f"[Visual: {concept.visual_description}]")

        lines.extend([
            "",
            "## Example",
            f"{script.example.text}",
            f"[Visual: {script.example.visual_description}]",
            "",
            "## Call to Action",
            f"{script.cta.text}",
            f"[Visual: {script.cta.visual_description}]",
        ])

        return "\n".join(lines)


# Singleton instance
script_generator = ScriptGenerator()
