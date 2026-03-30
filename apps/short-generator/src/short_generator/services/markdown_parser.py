"""Markdown Parser for Docusaurus Lessons.

This module parses markdown files from Docusaurus to extract:
- Chapter ID (from filename or frontmatter)
- Title (from first H1 or frontmatter)
- Content (cleaned of markdown syntax)
- Frontmatter metadata
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParsedChapter:
    """Represents a parsed markdown chapter.

    Attributes:
        id: Chapter identifier (from filename or frontmatter)
        title: Chapter title
        content: Cleaned content text
        frontmatter: Raw frontmatter dict
        word_count: Estimated word count
        reading_time_seconds: Estimated reading time
    """

    id: str
    title: str
    content: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    word_count: int = 0
    reading_time_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "frontmatter": self.frontmatter,
            "word_count": self.word_count,
            "reading_time_seconds": self.reading_time_seconds,
        }


class MarkdownParser:
    """Parses Docusaurus markdown files for video generation."""

    # Regex patterns
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
    H1_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```")
    INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    BOLD_PATTERN = re.compile(r"\*\*([^*]+)\*\*|__([^_]+)__")
    ITALIC_PATTERN = re.compile(r"\*([^*]+)\*|_([^_]+)_")
    HTML_COMMENT_PATTERN = re.compile(r"<!--[\s\S]*?-->")

    # Reading speed: ~200 words per minute
    WORDS_PER_MINUTE = 200

    def parse_file(self, file_path: str) -> ParsedChapter:
        """Parse a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            ParsedChapter object
        """
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        return self.parse_content(content, file_path)

    def parse_content(self, content: str, file_path: str | None = None) -> ParsedChapter:
        """Parse markdown content string.

        Args:
            content: Markdown content
            file_path: Optional file path for ID extraction

        Returns:
            ParsedChapter object
        """
        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)
        content_without_frontmatter = self.FRONTMATTER_PATTERN.sub("", content)

        # Extract title (from frontmatter or first H1)
        title = self._extract_title(frontmatter, content_without_frontmatter)

        # Extract ID (from frontmatter or filename)
        chapter_id = self._extract_id(frontmatter, file_path)

        # Clean content
        cleaned_content = self._clean_content(content_without_frontmatter)

        # Calculate stats
        word_count = self._count_words(cleaned_content)
        reading_time = (word_count / self.WORDS_PER_MINUTE) * 60  # seconds

        return ParsedChapter(
            id=chapter_id,
            title=title,
            content=cleaned_content,
            frontmatter=frontmatter,
            word_count=word_count,
            reading_time_seconds=reading_time,
        )

    def _extract_frontmatter(self, content: str) -> dict[str, Any]:
        """Extract YAML frontmatter from markdown.

        Args:
            content: Markdown content

        Returns:
            Frontmatter as dictionary
        """
        match = self.FRONTMATTER_PATTERN.search(content)
        if not match:
            return {}

        try:
            import yaml
            return yaml.safe_load(match.group(1)) or {}
        except ImportError:
            # If yaml not available, return empty dict
            return {}
        except Exception:
            return {}

    def _extract_title(self, frontmatter: dict[str, Any], content: str) -> str:
        """Extract title from frontmatter or first H1.

        Args:
            frontmatter: Parsed frontmatter
            content: Content without frontmatter

        Returns:
            Title string
        """
        # Try frontmatter first
        if "title" in frontmatter:
            return str(frontmatter["title"])

        if "sidebar_label" in frontmatter:
            return str(frontmatter["sidebar_label"])

        # Try first H1
        match = self.H1_PATTERN.search(content)
        if match:
            return match.group(1).strip()

        # Fallback
        return "Untitled"

    def _extract_id(self, frontmatter: dict[str, Any], file_path: str | None) -> str:
        """Extract chapter ID from frontmatter or filename.

        Args:
            frontmatter: Parsed frontmatter
            file_path: Optional file path

        Returns:
            Chapter ID string
        """
        # Try frontmatter
        if "id" in frontmatter:
            return str(frontmatter["id"])

        if "slug" in frontmatter:
            # Convert slug to ID
            return str(frontmatter["slug"]).strip("/").replace("/", "-")

        # Try filename
        if file_path:
            filename = Path(file_path).stem
            # Remove numeric prefix if present
            return re.sub(r"^\d+[-_]?", "", filename)

        return "unknown"

    def _clean_content(self, content: str) -> str:
        """Clean markdown content to plain text.

        Args:
            content: Markdown content

        Returns:
            Cleaned plain text
        """
        # Remove code blocks
        cleaned = self.CODE_BLOCK_PATTERN.sub("", content)

        # Remove HTML comments
        cleaned = self.HTML_COMMENT_PATTERN.sub("", cleaned)

        # Remove inline code (keep the text inside)
        cleaned = self.INLINE_CODE_PATTERN.sub(r"\1", cleaned)

        # Remove markdown links (keep the text)
        cleaned = self.LINK_PATTERN.sub(r"\1", cleaned)

        # Remove bold/italic markers
        cleaned = self.BOLD_PATTERN.sub(r"\1\2", cleaned)
        cleaned = self.ITALIC_PATTERN.sub(r"\1\2", cleaned)

        # Remove markdown headers
        cleaned = re.sub(r"^#+\s+", "", cleaned, flags=re.MULTILINE)

        # Clean up whitespace
        cleaned = re.sub(r"\n\n+", "\n\n", cleaned)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"^\s+|\s+$", "", cleaned, flags=re.MULTILINE)

        return cleaned.strip()

    def _count_words(self, text: str) -> int:
        """Count words in text.

        Args:
            text: Plain text

        Returns:
            Word count
        """
        # Simple word count by splitting on whitespace
        words = text.split()
        return len([w for w in words if w.strip()])


# Singleton instance
markdown_parser = MarkdownParser()


def parse_lesson_file(file_path: str) -> ParsedChapter:
    """Convenience function to parse a lesson file.

    Args:
        file_path: Path to markdown file

    Returns:
        ParsedChapter object
    """
    return markdown_parser.parse_file(file_path)


def get_lesson_excerpt(content: str, max_words: int = 50) -> str:
    """Get a short excerpt from lesson content.

    Useful for generating short video scripts from longer content.

    Args:
        content: Lesson content
        max_words: Maximum words in excerpt

    Returns:
        Excerpt text
    """
    words = content.split()
    if len(words) <= max_words:
        return content

    # Get first N words and end at sentence boundary
    excerpt_words = words[:max_words]
    excerpt = " ".join(excerpt_words)

    # Try to end at a sentence boundary
    for punct in [".", "!", "?"]:
        last_punct = excerpt.rfind(punct)
        if last_punct > len(excerpt) * 0.5:  # At least halfway through
            excerpt = excerpt[:last_punct + 1]
            break

    return excerpt
