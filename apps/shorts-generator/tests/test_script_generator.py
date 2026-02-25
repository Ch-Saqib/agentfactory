"""Tests for script generator service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from shorts_generator.services.content_extractor import LessonContent
from shorts_generator.services.script_generator import (
    GeneratedScript,
    ScriptGenerator,
    ScriptScene,
)


@pytest.fixture
def generator():
    """Create a script generator instance."""
    with patch("shorts_generator.services.script_generator.genai"):
        gen = ScriptGenerator()
        gen.model = MagicMock()
        yield gen


@pytest.fixture
def sample_lesson():
    """Create a sample lesson content."""
    return LessonContent(
        lesson_path="01-General-Agents-Foundations/01-agent-factory-paradigm/01-the-2025-inflection-point.md",
        frontmatter={
            "title": "The 2025 AI Inflection Point",
            "chapter": 1,
            "lesson": 1,
        },
        body="AI agents are transforming software development...",
        title="The 2025 AI Inflection Point",
        concepts=[
            MagicMock(title="What is an AI Agent", content="AI agents can reason and act", level=1, position=0),
            MagicMock(title="Why 2025 is Different", content="Three trends are converging", level=1, position=100),
        ],
        code_blocks=[],
        difficulty_level="beginner",
        word_count=500,
        is_suitable_for_short=True,
    )


def test_calculate_word_count(generator):
    """Test word count calculation for duration."""
    assert generator._calculate_word_count(60) == 150  # 2.5 words per second
    assert generator._calculate_word_count(30) == 75
    assert generator._calculate_word_count(90) == 225


def test_estimate_duration(generator):
    """Test duration estimation from word count."""
    assert generator._estimate_duration(150) == 60
    assert generator._estimate_duration(75) == 30
    assert generator._estimate_duration(10) == 5  # Minimum 5 seconds


def test_estimate_duration_minimum(generator):
    """Test that duration has minimum of 5 seconds."""
    assert generator._estimate_duration(0) == 5
    assert generator._estimate_duration(1) == 5


def test_build_generation_prompt(generator, sample_lesson):
    """Test prompt building for script generation."""
    prompt = generator._build_generation_prompt(sample_lesson, target_duration=60)

    assert "The 2025 AI Inflection Point" in prompt
    assert "60 seconds" in prompt
    assert "What is an AI Agent" in prompt
    assert "Hook (" in prompt
    assert "application/json" in prompt


@pytest.mark.asyncio
async def test_generate_script_success(generator, sample_lesson):
    """Test successful script generation."""
    # Mock Gemini response
    mock_response = MagicMock()
    mock_response.text = """{
  "hook": {"text": "Did you know 2025 is the biggest AI shift since the iPhone?", "visual": "Futuristic AI brain with glowing networks", "duration": 5},
  "concepts": [
    {"text": "AI agents can reason and act autonomously", "visual": "Robot thinking with neural pathways", "duration": 15},
    {"text": "They're not just chatbots - they build things", "visual": "AI constructing code on screen", "duration": 10}
  ],
  "example": {"text": "An AI agent recently got a perfect score at ICPC", "visual": "Trophy with AI robot celebrating", "duration": 20},
  "cta": {"text": "Read the full lesson to understand why 2025 matters", "visual": "Book cover with link button", "duration": 10}
}"""

    generator.model.generate_content_async = AsyncMock(return_value=mock_response)

    script = await generator.generate_script(sample_lesson, target_duration=60)

    assert script.lesson_title == "The 2025 AI Inflection Point"
    assert script.hook.text == "Did you know 2025 is the biggest AI shift since the iPhone?"
    assert script.hook.scene_type == "hook"
    assert len(script.concepts) == 2
    assert script.example.text == "An AI agent recently got a perfect score at ICPC"
    assert script.cta.text == "Read the full lesson to understand why 2025 matters"
    assert script.total_duration == 60  # 5 + 15 + 10 + 20 + 10


@pytest.mark.asyncio
async def test_generate_script_handles_json_error(generator, sample_lesson):
    """Test handling of invalid JSON response."""
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON"

    generator.model.generate_content_async = AsyncMock(return_value=mock_response)

    with pytest.raises(ValueError, match="Invalid JSON response"):
        await generator.generate_script(sample_lesson)


@pytest.mark.asyncio
async def test_generate_script_handles_missing_fields(generator, sample_lesson):
    """Test handling of response missing required fields."""
    mock_response = MagicMock()
    mock_response.text = '{"hook": {"text": "Hook"}, "concepts": []}'  # Missing example and cta

    generator.model.generate_content_async = AsyncMock(return_value=mock_response)

    with pytest.raises(ValueError, match="Invalid script structure"):
        await generator.generate_script(sample_lesson)


def test_validate_timing_within_tolerance(generator):
    """Test validation of script timing within tolerance."""
    script = GeneratedScript(
        lesson_path="test.md",
        lesson_title="Test",
        hook=ScriptScene("Hook", "Visual", 5, "hook"),
        concepts=[
            ScriptScene("Concept 1", "Visual", 25, "concept"),
            ScriptScene("Concept 2", "Visual", 10, "concept"),
        ],
        example=ScriptScene("Example", "Visual", 20, "example"),
        cta=ScriptScene("CTA", "Visual", 10, "cta"),
        total_duration=70,  # Within 10s tolerance of 60s target
        model_used="gemini-2.0-flash-exp",
    )

    assert generator.validate_timing(script) is True


def test_validate_timing_outside_tolerance(generator):
    """Test validation rejects scripts outside tolerance."""
    script = GeneratedScript(
        lesson_path="test.md",
        lesson_title="Test",
        hook=ScriptScene("Hook", "Visual", 5, "hook"),
        concepts=[],
        example=ScriptScene("Example", "Visual", 20, "example"),
        cta=ScriptScene("CTA", "Visual", 10, "cta"),
        total_duration=100,  # 40s over target - outside 10s tolerance
        model_used="gemini-2.0-flash-exp",
    )

    assert generator.validate_timing(script) is False


def test_format_for_tts(generator):
    """Test formatting script for text-to-speech."""
    script = GeneratedScript(
        lesson_path="test.md",
        lesson_title="Test Video",
        hook=ScriptScene("Hook text here", "Visual", 5, "hook"),
        concepts=[
            ScriptScene("Concept text", "Visual", 15, "concept"),
        ],
        example=ScriptScene("Example text", "Visual", 20, "example"),
        cta=ScriptScene("CTA text", "Visual", 10, "cta"),
        total_duration=50,
        model_used="gemini-2.0-flash-exp",
    )

    tts_text = generator.format_for_tts(script)

    assert "Hook text here" in tts_text
    assert "Concept text" in tts_text
    assert "Example text" in tts_text
    assert "CTA text" in tts_text


def test_get_script_text(generator):
    """Test getting full script as formatted text."""
    script = GeneratedScript(
        lesson_path="test.md",
        lesson_title="Test Video",
        hook=ScriptScene("Hook text", "Visual description", 5, "hook"),
        concepts=[
            ScriptScene("First concept", "Visual 1", 10, "concept"),
        ],
        example=ScriptScene("Example", "Visual 2", 15, "example"),
        cta=ScriptScene("Read more!", "Visual 3", 5, "cta"),
        total_duration=35,
        model_used="gemini-2.0-flash-exp",
    )

    script_text = generator.get_script_text(script)

    assert "# Test Video" in script_text
    assert "**Duration**: 35s" in script_text
    assert "## Hook" in script_text
    assert "Hook text" in script_text
    assert "[Visual: Visual description]" in script_text
    assert "## Concepts" in script_text
    assert "1. First concept" in script_text


def test_validate_timing_custom_tolerance(generator):
    """Test validation with custom tolerance."""
    script = GeneratedScript(
        lesson_path="test.md",
        lesson_title="Test",
        hook=ScriptScene("Hook", "Visual", 5, "hook"),
        concepts=[],
        example=ScriptScene("Example", "Visual", 20, "example"),
        cta=ScriptScene("CTA", "Visual", 10, "cta"),
        total_duration=85,  # 25s over 60s target
        model_used="gemini-2.0-flash-exp",
    )

    # Should fail with default 10s tolerance
    assert generator.validate_timing(script) is False

    # Should pass with 30s tolerance
    assert generator.validate_timing(script, tolerance_seconds=30) is True
