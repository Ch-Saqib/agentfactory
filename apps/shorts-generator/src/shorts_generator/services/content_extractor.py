"""Content Extractor Service for Lesson Shorts Generator.

This service parses lesson markdown content and extracts key information needed
for short video generation:
- Key concepts (2-5 per lesson)
- Code examples
- Difficulty level from frontmatter
- Validation for short generation suitability
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

import httpx
import yaml
from markdown import Markdown

from shorts_generator.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CodeBlock:
    """Represents a code block extracted from lesson content."""

    language: str
    code: str
    line_start: int
    line_end: int


@dataclass
class Concept:
    """Represents a key concept extracted from lesson content.

    Attributes:
        title: Concept title (usually from heading)
        content: Concept content/description
        level: Heading level (1-6)
        position: Position in document (character index)
    """

    title: str
    content: str
    level: int
    position: int


@dataclass
class LessonContent:
    """Represents parsed lesson content.

    Attributes:
        lesson_path: Original lesson path
        frontmatter: YAML frontmatter as dict
        body: Lesson body content (without frontmatter)
        title: Lesson title
        concepts: List of extracted key concepts
        code_blocks: List of code blocks
        difficulty_level: Detected difficulty (beginner, intermediate, advanced)
        word_count: Total word count
        is_suitable_for_short: Whether this lesson can generate a good short
    """

    lesson_path: str
    frontmatter: dict[str, Any]
    body: str
    title: str
    concepts: list[Concept]
    code_blocks: list[CodeBlock]
    difficulty_level: str
    word_count: int
    is_suitable_for_short: bool


class ContentExtractor:
    """Extracts structured content from lesson markdown."""

    def __init__(self):
        """Initialize the content extractor."""
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for GitHub fetches."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    def parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content.

        Args:
            content: Full markdown content, possibly with --- delimited frontmatter.

        Returns:
            Tuple of (frontmatter_dict, body_content).
            Returns ({}, content) if no frontmatter found.
            Returns ({}, content) on malformed YAML (graceful degradation).
        """
        if not content or not content.startswith("---"):
            return {}, content

        # Find the closing ---
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return {}, content

        frontmatter_str = content[3:end_idx].strip()
        body = content[end_idx + 3 :].lstrip("\n")

        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            if not isinstance(frontmatter, dict):
                return {}, body
            return frontmatter, body
        except yaml.YAMLError as e:
            logger.warning("Malformed YAML frontmatter: %s", e)
            return {}, body

    async def fetch_lesson_content(self, lesson_path: str) -> tuple[str, bool]:
        """Fetch lesson content from GitHub.

        Args:
            lesson_path: Path like "01-Part/02-chapter/03-lesson"

        Returns:
            Tuple of (content, success)
        """
        if not lesson_path:
            return "", False

        clean_path = lesson_path.strip("/")
        if not clean_path.startswith("apps/"):
            clean_path = f"apps/learn-app/docs/{clean_path}"

        # Try different extensions
        extensions = [""]
        if not clean_path.endswith((".md", ".mdx")):
            extensions = [".md", ".mdx"]

        client = await self._get_http_client()
        headers = {}
        if hasattr(settings, "github_token") and settings.github_token:
            headers["Authorization"] = f"token {settings.github_token}"

        for ext in extensions:
            url = f"https://raw.githubusercontent.com/panaversity/agentfactory/main/{clean_path}{ext}"

            try:
                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    logger.debug("Fetched content from GitHub: %s", url)
                    return response.text, True

            except Exception as e:
                logger.warning("Failed to fetch from GitHub %s: %s", url, e)
                continue

        return "", False

    def extract_headings(self, body: str) -> list[Concept]:
        """Extract headings as key concepts from lesson body.

        Args:
            body: Lesson body content (without frontmatter)

        Returns:
            List of Concept objects representing headings
        """
        concepts = []
        lines = body.split("\n")
        current_position = 0

        for line in lines:
            # Match ATX-style headings (#, ##, ###, etc.)
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                # Remove any markdown formatting from title
                title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)  # Bold
                title = re.sub(r'``(.+?)``', r'\1', title)  # Code
                title = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', title)  # Links

                concepts.append(
                    Concept(
                        title=title,
                        content="",  # Will be populated by extract_concept_content
                        level=level,
                        position=current_position,
                    )
                )

            current_position += len(line) + 1  # +1 for newline

        return concepts

    def extract_concept_content(self, body: str, concepts: list[Concept]) -> list[Concept]:
        """Extract content for each concept (heading + following paragraphs).

        Args:
            body: Lesson body content
            concepts: List of concepts with positions

        Returns:
            Updated list of concepts with content populated
        """
        if not concepts:
            return []

        # Sort concepts by position
        sorted_concepts = sorted(concepts, key=lambda c: c.position)
        updated_concepts = []

        for i, concept in enumerate(sorted_concepts):
            # Find content between this heading and next heading
            start_pos = concept.position
            end_pos = (
                sorted_concepts[i + 1].position if i + 1 < len(sorted_concepts) else len(body)
            )

            content = body[start_pos:end_pos].strip()
            # Remove the heading line itself
            content = "\n".join(content.split("\n")[1:]).strip()

            # Limit content length (first 500 chars)
            if len(content) > 500:
                content = content[:500] + "..."

            updated_concepts.append(
                Concept(
                    title=concept.title,
                    content=content,
                    level=concept.level,
                    position=concept.position,
                )
            )

        return updated_concepts

    def extract_code_blocks(self, body: str) -> list[CodeBlock]:
        """Extract code blocks from lesson content.

        Args:
            body: Lesson body content

        Returns:
            List of CodeBlock objects
        """
        code_blocks = []
        lines = body.split("\n")

        in_code_block = False
        code_lang = ""
        code_lines = []
        line_start = 0
        current_line = 0

        for line in lines:
            # Check for fenced code block start
            if not in_code_block and line.strip().startswith("```"):
                in_code_block = True
                code_lang = line.strip()[3:] or "text"
                code_lines = []
                line_start = current_line
                current_line += 1
                continue

            # Check for fenced code block end
            if in_code_block and line.strip() == "```":
                code_blocks.append(
                    CodeBlock(
                        language=code_lang,
                        code="\n".join(code_lines),
                        line_start=line_start,
                        line_end=current_line,
                    )
                )
                in_code_block = False
                code_lang = ""
                code_lines = []
                current_line += 1
                continue

            # Collect code lines
            if in_code_block:
                code_lines.append(line)

            current_line += 1

        return code_blocks

    def detect_difficulty_level(self, frontmatter: dict[str, Any]) -> str:
        """Detect lesson difficulty from frontmatter.

        Args:
            frontmatter: Parsed frontmatter dictionary

        Returns:
            Difficulty level: beginner, intermediate, or advanced
        """
        # Check for explicit difficulty in skills
        if "skills" in frontmatter:
            for skill in frontmatter["skills"]:
                if isinstance(skill, dict):
                    prof_level = skill.get("proficiency_level", "").lower()
                    if "beginner" in prof_level or "a1" in prof_level:
                        return "beginner"
                    elif "advanced" in prof_level or "c1" in prof_level or "c2" in prof_level:
                        return "advanced"

        # Check cognitive load
        if "cognitive_load" in frontmatter:
            new_concepts = frontmatter["cognitive_load"].get("new_concepts", 0)
            if new_concepts <= 2:
                return "beginner"
            elif new_concepts >= 5:
                return "advanced"

        # Check chapter number (higher chapters = more advanced)
        if "chapter" in frontmatter:
            chapter_num = frontmatter["chapter"]
            if isinstance(chapter_num, int):
                if chapter_num <= 3:
                    return "beginner"
                elif chapter_num >= 20:
                    return "advanced"

        return "intermediate"  # Default

    def validate_lesson_suitability(self, content: LessonContent) -> tuple[bool, str]:
        """Validate if lesson is suitable for short video generation.

        Args:
            content: Parsed lesson content

        Returns:
            Tuple of (is_suitable, reason)
        """
        # Check minimum word count
        if content.word_count < 100:
            return False, "Lesson too short (< 100 words)"

        # Check if we have enough concepts
        if len(content.concepts) < 2:
            return False, "Not enough key concepts (< 2 headings)"

        # Check if lesson has useful content
        if not content.concepts and not content.code_blocks:
            return False, "No extractable concepts or code examples"

        return True, "Suitable for short generation"

    def extract_key_concepts(self, concepts: list[Concept], max_concepts: int = 5) -> list[Concept]:
        """Extract the most important concepts for short video.

        Prioritizes:
        1. Top-level headings (level 1-2)
        2. Conceptual headings (not "Try With AI", "Exercises", etc.)
        3. First few concepts (early in lesson)

        Args:
            concepts: All extracted concepts
            max_concepts: Maximum number of concepts to return

        Returns:
            Filtered list of key concepts
        """
        # Filter out non-conceptual headings
        skip_patterns = [
            "try with ai",
            "exercise",
            "practice",
            "assignment",
            "summary",
            "conclusion",
            "next steps",
            "resources",
            "further reading",
        ]

        key_concepts = []
        for concept in concepts:
            # Skip if title matches skip pattern
            if any(pattern in concept.title.lower() for pattern in skip_patterns):
                continue

            # Prioritize level 1-2 headings
            if concept.level <= 2:
                key_concepts.append(concept)
            elif len(key_concepts) < max_concepts:
                # Add level 3+ headings if we need more concepts
                key_concepts.append(concept)

            if len(key_concepts) >= max_concepts:
                break

        return key_concepts[:max_concepts]

    async def extract_content(self, lesson_path: str) -> LessonContent | None:
        """Extract and parse all content from a lesson.

        Args:
            lesson_path: Path to the lesson (e.g., "01-Part/02-Chapter/03-Lesson.md")

        Returns:
            LessonContent object with all extracted information, or None if fetch fails
        """
        # Fetch content from GitHub
        raw_content, success = await self.fetch_lesson_content(lesson_path)
        if not success:
            logger.error("Failed to fetch lesson: %s", lesson_path)
            return None

        # Parse frontmatter
        frontmatter, body = self.parse_frontmatter(raw_content)

        # Extract title
        title = frontmatter.get("title", "")
        if not title:
            # Try to extract from first heading
            match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if match:
                title = match.group(1).strip()
            else:
                title = lesson_path.split("/")[-1].replace("-", " ").title()

        # Extract concepts
        all_concepts = self.extract_headings(body)
        concepts_with_content = self.extract_concept_content(body, all_concepts)
        key_concepts = self.extract_key_concepts(concepts_with_content)

        # Extract code blocks
        code_blocks = self.extract_code_blocks(body)

        # Detect difficulty
        difficulty = self.detect_difficulty_level(frontmatter)

        # Count words
        word_count = len(body.split())

        # Validate suitability
        is_suitable, reason = self.validate_lesson_suitability(
            LessonContent(
                lesson_path=lesson_path,
                frontmatter=frontmatter,
                body=body,
                title=title,
                concepts=key_concepts,
                code_blocks=code_blocks,
                difficulty_level=difficulty,
                word_count=word_count,
                is_suitable_for_short=True,  # Placeholder
            )
        )

        return LessonContent(
            lesson_path=lesson_path,
            frontmatter=frontmatter,
            body=body,
            title=title,
            concepts=key_concepts,
            code_blocks=code_blocks,
            difficulty_level=difficulty,
            word_count=word_count,
            is_suitable_for_short=is_suitable,
        )


# Singleton instance
content_extractor = ContentExtractor()
