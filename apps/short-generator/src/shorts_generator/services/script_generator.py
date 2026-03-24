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
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from google import genai

from shorts_generator.core.config import settings
from shorts_generator.services.content_extractor import LessonContent

logger = logging.getLogger(__name__)

# Average speaking rate: 150 words per minute = 2.5 words per second
WORDS_PER_SECOND = 2.5


def is_incomplete_json(json_str: str) -> bool:
    """Check if JSON appears to be incomplete/truncated.

    Signs of incomplete JSON:
    - Unclosed brackets/braces
    - Unterminated strings
    - Trailing comma without value after it

    Args:
        json_str: JSON string to check

    Returns:
        True if JSON appears incomplete
    """
    if not json_str:
        return True

    json_str = json_str.strip()

    # Check bracket/brace balance
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    open_brackets = json_str.count('[')
    close_brackets = json_str.count(']')

    if open_braces != close_braces or open_brackets != close_brackets:
        return True

    # Check for unterminated strings (count odd number of unescaped quotes in value position)
    # This is a simple heuristic - not perfect but catches most cases
    lines = json_str.split('\n')
    for line in lines:
        # Skip lines that are just structure (braces, brackets, commas)
        stripped = line.strip()
        if stripped in ['{', '}', '[', ']', '', ',', '},', '],', '{,', '[,']:
            continue
        # If line has a quote but no closing quote, likely unterminated
        if stripped.count('"') % 2 != 0:
            return True

    # Check for trailing comma at the very end (common truncation point)
    if json_str.rstrip().endswith(','):
        return True

    return False


def repair_json(json_str: str) -> str:
    """Repair common JSON issues from LLM responses.

    Fixes:
    - Trailing commas in objects/arrays
    - Single quotes instead of double quotes
    - Unquoted keys
    - Comments (both // and /* */ style)
    - Missing commas between objects
    - Control characters

    Args:
        json_str: Potentially malformed JSON string

    Returns:
        Repaired JSON string
    """
    if not json_str:
        return "{}"

    text = json_str

    # Remove control characters that can break JSON parsing
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # Remove // single-line comments
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)

    # Remove /* */ multi-line comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

    # Fix trailing commas in objects {a: 1,} -> {a: 1}
    text = re.sub(r',\s*}', '}', text)

    # Fix trailing commas in arrays [1,] -> [1]
    text = re.sub(r',\s*]', ']', text)

    # Fix single quotes to double quotes for keys 'key': -> "key":
    text = re.sub(r"'([^']+)'(\s*:)", r'"\1"\2', text)

    # Fix single quotes to double quotes for values : 'value' -> : "value"
    # This is more complex - we need to be careful about nested quotes
    # Only replace single quotes that are NOT preceded by a backslash
    # and are within JSON value positions
    def replace_single_quotes_in_values(match):
        """Replace single quotes in string values with double quotes."""
        content = match.group(1)
        # Escape existing double quotes
        content = content.replace('"', '\\"')
        return f'"{content}"'

    # Pattern for : '...' or :  '...'  values
    text = re.sub(r':\s*\'([^\']+)\'', replace_single_quotes_in_values, text)

    # Fix unquoted keys like key: "value" -> "key": "value"
    # Match identifiers followed by colon, but not if already quoted
    text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', text)

    # Fix missing commas between key-value pairs in objects
    # This pattern looks for } followed by "key" without comma
    text = re.sub(r'}\s*"', '}, "', text)

    # Fix missing commas between array elements
    # This pattern looks for } followed by { without comma
    text = re.sub(r'}\s*{', '}, {', text)

    # Fix missing commas between string elements in arrays
    # This pattern looks for "item1" followed by "item2" without comma
    text = re.sub(r'"([^"]+)"\s+"([^"]+)"', r'"\1", "\2"', text)

    return text


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
    """Generates short video scripts using multiple LLM providers.

    Supported providers:
    - gemini: Google Gemini API
    - groq: Groq with Llama models (best free tier)
    - openai: OpenAI GPT models
    """

    def __init__(self):
        """Initialize the script generator with configured provider."""
        self.provider = getattr(settings, 'script_provider', 'groq').lower()

        if self.provider == "gemini":
            self.client = genai.Client(api_key=settings.gemini_api_key)
            self.model = settings.gemini_model
        elif self.provider == "groq":
            from groq import Groq
            self.client = Groq(api_key=getattr(settings, 'groq_api_key', None))
            self.model = settings.groq_model
        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=getattr(settings, 'openai_api_key', None))
            self.model = settings.openai_model
        else:
            logger.warning(f"Unknown provider '{self.provider}', falling back to groq")
            from groq import Groq
            self.provider = "groq"
            self.client = Groq(api_key=getattr(settings, 'groq_api_key', None))
            self.model = "llama-3.3-70b-versatile"

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
- CTA must say something like "Check out the full lesson to learn more" (natural, spoken language)
- Visual descriptions should be specific enough for AI image generation (e.g., "Futuristic AI brain network with glowing purple and blue neural connections on dark background")
- CRITICAL: The "text" fields will be read aloud by a text-to-speech engine. They MUST contain ONLY natural spoken English:
  - NO slashes (write "or" instead of "/")
  - NO brackets, parentheses, or square brackets
  - NO URLs or links
  - NO markdown formatting (no *, #, `, etc.)
  - NO code syntax, file paths, or technical notation
  - NO abbreviations that sound odd when spoken (spell them out)
  - Write exactly how a human narrator would say it

Respond with ONLY the JSON object, nothing else:"""

        return prompt

    def _build_simple_prompt(
        self,
        lesson: LessonContent,
        target_duration: int = 60,
    ) -> str:
        """Build a simplified prompt for script generation (to avoid truncation).

        Uses single concept scenes and shorter descriptions.

        Args:
            lesson: Parsed lesson content
            target_duration: Target duration in seconds

        Returns:
            Prompt string for Gemini
        """
        # Use simpler structure with single concept
        prompt = f"""Generate a short video script for: {lesson.title}

Create JSON with this exact structure:
{{
  "hook": {{"text": "Attention-grabbing question", "visual": "AI tech visual", "duration": 5}},
  "concepts": [
    {{"text": "Main explanation", "visual": "Tech visual", "duration": 30}}
  ],
  "example": {{"text": "Concrete example", "visual": "Diagram visual", "duration": 15}},
  "cta": {{"text": "Read full lesson for more", "visual": "Cover visual", "duration": 10}}
}}

Keep all descriptions brief. Respond with ONLY raw JSON."""

        return prompt

    async def _generate_with_gemini(
        self,
        prompt: str,
        lesson: LessonContent,
        target_duration: int,
    ) -> dict:
        """Generate script using Google Gemini API."""
        import asyncio

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
        )

        response_text = response.text
        logger.info(f"Gemini response length: {len(response_text)}")
        return self._parse_response(response_text, lesson, target_duration, "gemini")

    async def _generate_with_groq(
        self,
        prompt: str,
        lesson: LessonContent,
        target_duration: int,
    ) -> dict:
        """Generate script using Groq API with Llama models."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content
        logger.info(f"Groq response length: {len(response_text)}")
        return self._parse_response(response_text, lesson, target_duration, "groq")

    async def _generate_with_openai(
        self,
        prompt: str,
        lesson: LessonContent,
        target_duration: int,
    ) -> dict:
        """Generate script using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content
        logger.info(f"OpenAI response length: {len(response_text)}")
        return self._parse_response(response_text, lesson, target_duration, "openai")

    def _parse_response(
        self,
        response_text: str,
        lesson: LessonContent,
        target_duration: int,
        provider: str,
    ) -> dict:
        """Parse and validate LLM response into script data.

        Args:
            response_text: Raw response from LLM
            lesson: Original lesson content
            target_duration: Target duration
            provider: Provider name for logging

        Returns:
            Parsed script data dictionary

        Raises:
            ValueError: If parsing fails
        """
        import asyncio

        logger.debug(f"{provider} response preview: {response_text[:200]}...")

        # Extract JSON from response (handle markdown code blocks)
        json_text = response_text.strip()

        # Remove markdown code blocks if present
        if json_text.startswith("```"):
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

        # Check for incomplete JSON and retry if needed
        if is_incomplete_json(json_text):
            logger.warning(f"Response appears truncated. Retrying with simplified prompt...")
            prompt = self._build_simple_prompt(lesson, target_duration)

            if self.provider == "gemini":
                response = asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.model,
                    contents=prompt,
                    config={
                        "temperature": 0.7,
                        "max_output_tokens": 8192,
                        "response_mime_type": "application/json",
                    },
                )
                response_text = response.result().text
            elif self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                    response_format={"type": "json_object"},
                )
                response_text = response.choices[0].message.content
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                    response_format={"type": "json_object"},
                )
                response_text = response.choices[0].message.content

            json_text = response_text.strip()
            if json_text.startswith("```"):
                lines = json_text.split("\n")
                if lines[0].startswith("```json"):
                    lines = lines[1:]
                elif lines[0].startswith("```"):
                    lines = lines[1:]
                for i, line in enumerate(lines):
                    if line.strip() == "```":
                        lines = lines[:i]
                        break
                json_text = "\n".join(lines).strip()

        # Parse with JSON repair
        script_data = None
        parse_errors = []

        try:
            script_data = json.loads(json_text)
        except json.JSONDecodeError as e1:
            parse_errors.append(f"Direct parse failed: {e1}")
            logger.warning(f"Direct JSON parse failed, attempting repair: {e1}")

            try:
                repaired = repair_json(json_text)
                script_data = json.loads(repaired)
                logger.info("Successfully parsed with JSON repair")
            except json.JSONDecodeError as e2:
                parse_errors.append(f"Repair parse failed: {e2}")
                logger.error(f"JSON repair also failed. Errors: {parse_errors}")
                logger.error(f"Failed JSON content (first 500 chars): {json_text[:500]}")
                raise ValueError(
                    f"Failed to parse {provider} JSON response. "
                    f"Errors: {'; '.join(parse_errors)}"
                ) from e1

        # Validate structure
        if not all(key in script_data for key in ["hook", "concepts", "example", "cta"]):
            raise ValueError(f"Invalid script structure from {provider}")

        return script_data

    async def generate_script(
        self,
        lesson: LessonContent,
        target_duration: int = 60,
    ) -> GeneratedScript:
        """Generate a script from lesson content.

        Routes to the appropriate provider based on settings.script_provider.

        Args:
            lesson: Parsed lesson content
            target_duration: Target duration in seconds (default: 60)

        Returns:
            GeneratedScript object with all scenes

        Raises:
            Exception: If generation fails
        """
        logger.info(f"Generating script for: {lesson.lesson_path} using {self.provider}")

        # Build prompt
        prompt = self._build_generation_prompt(lesson, target_duration)

        try:
            # Route to appropriate provider
            if self.provider == "gemini":
                script_data = await self._generate_with_gemini(prompt, lesson, target_duration)
            elif self.provider == "groq":
                script_data = await self._generate_with_groq(prompt, lesson, target_duration)
            elif self.provider == "openai":
                script_data = await self._generate_with_openai(prompt, lesson, target_duration)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")

            # Create script objects from parsed data
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
                model_used=f"{self.provider}:{self.model}",
            )

            logger.info(f"Script generated successfully: {total_duration}s target duration")

            return generated_script

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            raise ValueError(f"Invalid JSON response from {self.provider}: {e}") from e
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

    @staticmethod
    def _sanitize_for_speech(text: str) -> str:
        """Strip non-speakable artefacts so TTS receives clean text.

        Removes markdown, URLs, brackets, slashes-between-words, and
        other formatting that would be read aloud literally.
        """
        t = text

        # Remove markdown bold/italic markers
        t = re.sub(r'\*{1,3}', '', t)

        # Remove markdown headers (# ## ###)
        t = re.sub(r'^#{1,6}\s*', '', t, flags=re.MULTILINE)

        # Remove markdown links [text](url) -> text
        t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)

        # Remove raw URLs (http:// or https://)
        t = re.sub(r'https?://\S+', '', t)

        # Remove square-bracket placeholders like [link], [code], etc.
        t = re.sub(r'\[[^\]]*\]', '', t)

        # Remove parenthetical asides like (e.g., ...)
        t = re.sub(r'\([^)]{0,60}\)', '', t)

        # Replace slash-separated words like "API/webhook" -> "API or webhook"
        t = re.sub(r'(\w)/(\w)', r'\1 or \2', t)

        # Remove stray backticks
        t = t.replace('`', '')

        # Remove stray angle brackets
        t = re.sub(r'[<>]', '', t)

        # Collapse whitespace
        t = re.sub(r'\s+', ' ', t).strip()

        return t

    def format_for_tts(self, script: GeneratedScript) -> str:
        """Format script for text-to-speech generation.

        Combines all scenes into a single text, sanitized for TTS.

        Args:
            script: Generated script

        Returns:
            Clean spoken text for TTS
        """
        parts = []

        # Hook
        parts.append(script.hook.text)

        # Concepts
        for concept in script.concepts:
            parts.append(concept.text)

        # Example
        parts.append(script.example.text)

        # CTA
        parts.append(script.cta.text)

        raw = " ".join(parts)
        return self._sanitize_for_speech(raw)

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
