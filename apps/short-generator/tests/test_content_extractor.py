"""Tests for content extractor service."""

import pytest
from unittest.mock import AsyncMock, patch

from shorts_generator.services.content_extractor import (
    CodeBlock,
    Concept,
    ContentExtractor,
    LessonContent,
)


@pytest.fixture
def extractor():
    """Create a content extractor instance."""
    return ContentExtractor()


def test_parse_frontmatter_with_valid_yaml(extractor):
    """Test parsing valid YAML frontmatter."""
    content = """---
title: "Test Lesson"
chapter: 1
lesson: 1
difficulty: beginner
---
# Lesson Body

Some content here.
"""
    frontmatter, body = extractor.parse_frontmatter(content)

    assert frontmatter["title"] == "Test Lesson"
    assert frontmatter["chapter"] == 1
    assert frontmatter["lesson"] == 1
    assert frontmatter["difficulty"] == "beginner"
    assert "Lesson Body" in body


def test_parse_frontmatter_no_frontmatter(extractor):
    """Test parsing content without frontmatter."""
    content = "# Just a heading\n\nSome content."

    frontmatter, body = extractor.parse_frontmatter(content)

    assert frontmatter == {}
    assert "# Just a heading" in body


def test_parse_frontmatter_malformed_yaml(extractor):
    """Test graceful degradation on malformed YAML."""
    content = """---
title: "Unclosed string
---
Some content."""

    frontmatter, body = extractor.parse_frontmatter(content)

    # Should return empty dict on malformed YAML
    assert frontmatter == {}


def test_extract_headings(extractor):
    """Test extracting headings as concepts."""
    body = """
# Main Concept

Some content here.

## Sub Concept

More content.

### Deep Dive

Even more content.
"""

    concepts = extractor.extract_headings(body)

    assert len(concepts) == 3
    assert concepts[0].title == "Main Concept"
    assert concepts[0].level == 1
    assert concepts[1].title == "Sub Concept"
    assert concepts[1].level == 2
    assert concepts[2].title == "Deep Dive"
    assert concepts[2].level == 3


def test_extract_concept_content(extractor):
    """Test extracting content for each concept."""
    body = """
# First Concept

Content for first concept.

# Second Concept

Content for second concept.
"""

    concepts = extractor.extract_headings(body)
    concepts_with_content = extractor.extract_concept_content(body, concepts)

    assert len(concepts_with_content) == 2
    assert "Content for first concept" in concepts_with_content[0].content
    assert "Content for second concept" in concepts_with_content[1].content


def test_extract_code_blocks(extractor):
    """Test extracting code blocks."""
    body = """
Some text before.

```python
def hello():
    print("world")
```

More text.

```javascript
function greet() {
    console.log("hi");
}
```

End of content.
"""

    code_blocks = extractor.extract_code_blocks(body)

    assert len(code_blocks) == 2
    assert code_blocks[0].language == "python"
    assert "def hello():" in code_blocks[0].code
    assert code_blocks[1].language == "javascript"
    assert "function greet()" in code_blocks[1].code


def test_detect_difficulty_from_skills(extractor):
    """Test detecting difficulty from proficiency level."""
    frontmatter = {
        "skills": [
            {
                "name": "Python Basics",
                "proficiency_level": "A1",
            }
        ]
    }

    difficulty = extractor.detect_difficulty_level(frontmatter)
    assert difficulty == "beginner"


def test_detect_difficulty_from_cognitive_load(extractor):
    """Test detecting difficulty from cognitive load."""
    frontmatter = {
        "cognitive_load": {
            "new_concepts": 1,
        }
    }

    difficulty = extractor.detect_difficulty_level(frontmatter)
    assert difficulty == "beginner"


def test_detect_difficulty_from_chapter(extractor):
    """Test detecting difficulty from chapter number."""
    frontmatter = {
        "chapter": 25,
    }

    difficulty = extractor.detect_difficulty_level(frontmatter)
    assert difficulty == "intermediate"


def test_detect_difficulty_default(extractor):
    """Test default difficulty when no indicators present."""
    frontmatter = {}

    difficulty = extractor.detect_difficulty_level(frontmatter)
    assert difficulty == "intermediate"


def test_validate_lesson_suitable(extractor):
    """Test validation of suitable lesson."""
    content = LessonContent(
        lesson_path="test.md",
        frontmatter={},
        body="A" * 500,  # Long enough
        title="Test",
        concepts=[Concept("Concept 1", "", 1, 0), Concept("Concept 2", "", 1, 100)],
        code_blocks=[CodeBlock("python", "print('hi')", 10, 12)],
        difficulty_level="intermediate",
        word_count=500,
        is_suitable_for_short=True,
    )

    is_suitable, reason = extractor.validate_lesson_suitability(content)

    assert is_suitable is True
    assert "Suitable" in reason


def test_validate_lesson_too_short(extractor):
    """Test validation rejects too-short lesson."""
    content = LessonContent(
        lesson_path="test.md",
        frontmatter={},
        body="Short",
        title="Test",
        concepts=[],
        code_blocks=[],
        difficulty_level="beginner",
        word_count=1,
        is_suitable_for_short=True,
    )

    is_suitable, reason = extractor.validate_lesson_suitability(content)

    assert is_suitable is False
    assert "too short" in reason.lower()


def test_extract_key_concepts_limits_results(extractor):
    """Test that key concepts extraction respects max limit."""
    concepts = [
        Concept("Concept 1", "", 1, 0),
        Concept("Concept 2", "", 1, 100),
        Concept("Concept 3", "", 1, 200),
        Concept("Try With AI", "", 2, 300),  # Should be skipped
        Concept("Concept 4", "", 1, 400),
        Concept("Concept 5", "", 1, 500),
        Concept("Concept 6", "", 1, 600),
    ]

    key_concepts = extractor.extract_key_concepts(concepts, max_concepts=4)

    assert len(key_concepts) == 4
    assert all("Try With AI" not in c.title for c in key_concepts)


def test_extract_key_concepts_skips_exercises(extractor):
    """Test that exercise sections are skipped."""
    concepts = [
        Concept("Main Concept", "", 1, 0),
        Concept("Exercise 1", "", 2, 100),
        Concept("Practice Problem", "", 2, 200),
        Concept("Summary", "", 1, 300),
    ]

    key_concepts = extractor.extract_key_concepts(concepts, max_concepts=5)

    # Should skip Exercise, Practice, Summary
    assert len(key_concepts) == 1
    assert key_concepts[0].title == "Main Concept"


@pytest.mark.asyncio
async def test_extract_content_full_flow(extractor):
    """Test full content extraction flow with mocked GitHub fetch."""
    mock_content = """---
title: "AI Agents Foundation"
chapter: 1
lesson: 1
skills:
  - name: "AI Concepts"
    proficiency_level: "A1"
---

# What is an AI Agent?

AI agents are systems that can reason and act autonomously.

## Key Characteristics

AI agents have several important characteristics.

### Autonomy

They can operate independently.

### Perception

They can understand their environment.

```python
def agent_act():
    return "action"
```

## Try With AI

Practice creating your first agent.
"""

    with patch.object(extractor, "fetch_lesson_content", return_value=(mock_content, True)):
        content = await extractor.extract_content("01-General-Agents-Foundations/01-agent-factory-paradigm/01-the-2025-inflection-point.md")

        assert content is not None
        assert content.title == "AI Agents Foundation"
        assert content.difficulty_level == "beginner"
        assert content.word_count > 50
        assert len(content.concepts) > 0
        assert len(content.code_blocks) > 0
        assert content.is_suitable_for_short is True


@pytest.mark.asyncio
async def test_extract_content_handles_fetch_failure(extractor):
    """Test that fetch failure returns None."""
    with patch.object(extractor, "fetch_lesson_content", return_value=("", False)):
        content = await extractor.extract_content("nonexistent/lesson.md")

        assert content is None
