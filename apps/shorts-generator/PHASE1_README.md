# Phase 1: Audio Generation Pipeline - Google Cloud TTS

## Overview

This module implements Phase 1 of the video generation pipeline: **Audio Generation with Word-Level Timing Data** using Google Cloud Text-to-Speech API.

### Features

- ✅ **High-quality neural voices** - Natural-sounding speech
- ✅ **Word-level timing data** - Precise timepoints for each word
- ✅ **SSML support** - Advanced speech effects (emphasis, pauses, pitch)
- ✅ **Multiple audio formats** - MP3, WAV, OGG_OPUS
- ✅ **Duration detection** - Accurate audio duration using ffprobe
- ✅ **Production-ready** - Error handling, type hints, async support

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Google Cloud TTS Service | `google_tts_audio.py` | Generate audio with word timing |
| Markdown Parser | `markdown_parser.py` | Parse Docusaurus lesson files |
| Config Updates | `core/config.py` | Google Cloud settings |
| Tests | `tests/test_google_tts_audio.py` | Comprehensive test suite |
| Timing Test Script | `scripts/test_timing_accuracy.py` | Manual timing verification |

## Installation

### 1. Install Dependencies

```bash
cd apps/shorts-generator
uv sync
```

### 2. Set Up Google Cloud Credentials

```bash
# Option 1: Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Option 2: Add to .env file
echo "GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json" >> .env
```

### 3. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a service account
3. Grant "Cloud Text-to-Speech API User" role
4. Download JSON key file
5. Set path as `GOOGLE_APPLICATION_CREDENTIALS`

## Quick Start

### Basic Usage

```python
from shorts_generator.services.google_tts_audio import google_tts_generator

# Generate audio with word-level timing
result = google_tts_generator.generate(
    "Hello world! This is a test of word-level timing."
)

# Access results
print(f"Audio: {result.audio_path}")
print(f"Duration: {result.duration_seconds:.2f}s")
print(f"Words: {len(result.word_timings)}")

# Save timing data to JSON
result.save_timing_json("timing.json")
```

### Parse Markdown and Generate Audio

```python
from shorts_generator.services.markdown_parser import parse_lesson_file
from shorts_generator.services.google_tts_audio import google_tts_generator

# Parse lesson markdown
chapter = parse_lesson_file("path/to/lesson.md")

# Get excerpt for short video
excerpt = get_lesson_excerpt(chapter.content, max_words=50)

# Generate audio
result = google_tts_generator.generate(excerpt)

print(f"Generated {result.duration_seconds:.2f}s of audio")
```

## API Reference

### GoogleCloudTTSGenerator

#### Constructor

```python
GoogleCloudTTSGenerator(
    credentials_path: str | None = None,
    voice_preset: str = "narration_male",
    encoding: AudioEncoding = "MP3",
    sample_rate: int = 24000,
)
```

**Voice Presets:**
- `narration_male` - Male voice (en-US-Neural2-C)
- `narration_female` - Female voice (en-US-Neural2-A)
- `news` - News style (en-US-News-K)
- `casual` - Casual, friendly (en-US-Neural2-F)
- `dramatic` - British, dramatic (en-GB-Neural2-B)

#### Methods

##### `generate()`

Generate audio with word-level timing.

```python
result = generator.generate(
    text: str,
    speaking_rate: float = 1.0,  # 0.25 to 4.0
    pitch: float = 0.0,           # -20.0 to 20.0 semitones
    custom_voice: str | None = None,
    ssml: bool = False,
    output_path: str | None = None,
) -> GoogleTTSResult
```

##### `generate_with_ssml()`

Generate audio from SSML with advanced effects.

```python
ssml = '<speak><emphasis level="strong">Welcome</emphasis> to the <break time="500ms"/>AI Agent Factory.</speak>'
result = generator.generate_with_ssml(ssml)
```

### GoogleTTSResult

```python
@dataclass
class GoogleTTSResult:
    audio_path: str                    # Path to audio file
    duration_seconds: float            # Audio duration
    word_timings: list[WordTiming]     # Word-level timings
    voice_used: str                    # Voice name
    encoding: AudioEncoding            # Format (MP3, WAV, etc.)
    sample_rate: int                   # Sample rate in Hz
```

### WordTiming

```python
@dataclass
class WordTiming:
    word: str          # The spoken word
    start_time: float  # Start time in seconds
    end_time: float    # End time in seconds
```

## Configuration

Add to `.env` file:

```bash
# TTS Provider: "edge_tts" (free) or "google_tts" (paid, better timing)
TTS_PROVIDER=google_tts

# Google Cloud Settings
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GOOGLE_PROJECT_ID=your-project-id

# Voice Settings
GOOGLE_TTS_VOICE_PRESET=narration_male
GOOGLE_TTS_ENCODING=MP3
GOOGLE_TTS_SAMPLE_RATE=24000
```

## Testing

### Run All Tests

```bash
cd apps/shorts-generator
uv run pytest tests/test_google_tts_audio.py -v
```

### Run Timing Accuracy Test

```bash
# Manual test with real API
cd apps/shorts-generator
python scripts/test_timing_accuracy.py
```

### Skip Integration Tests

```bash
# Run only unit tests (no API calls)
uv run pytest tests/test_google_tts_audio.py -v -m "not integration"
```

## Timing Data Format

The timing JSON contains:

```json
{
  "duration": 5.234,
  "voice": "en-US-Neural2-C",
  "words": [
    {"word": "Hello", "start": 0.0, "end": 0.35},
    {"word": "world", "start": 0.35, "end": 0.62},
    {"word": "this", "start": 0.62, "end": 0.85},
    {"word": "is", "start": 0.85, "end": 1.02},
    {"word": "a", "start": 1.02, "end": 1.15},
    {"word": "test", "start": 1.15, "end": 1.48}
  ],
  "raw_timepoints": [
    {"text": "Hello", "time_seconds": 0.0},
    {"text": "world", "time_seconds": 0.35}
  ]
}
```

## Cost Estimation

Google Cloud TTS pricing (as of 2025):

| Voice Type | Cost per 1M chars | Cost per 60s video* |
|------------|-------------------|---------------------|
| Standard | $4.00 | ~$0.002 |
| Wavenet | $16.00 | ~$0.008 |
| Neural2 | $16.00 | ~$0.008 |

*Based on ~150 words per 60-second video.

**Example cost breakdown:**
- 60-second video (~150 words) using Neural2: ~$0.008
- 100 videos: ~$0.80
- 1,000 videos: ~$8.00

## Error Handling

```python
from shorts_generator.services.google_tts_audio import GoogleCloudTTSGenerator

generator = GoogleCloudTTSGenerator()

try:
    result = generator.generate("Test text")
except Exception as e:
    if "credentials" in str(e).lower():
        print("❌ Google Cloud credentials not configured")
        print("Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    elif "quota" in str(e).lower():
        print("❌ API quota exceeded")
    else:
        print(f"❌ TTS generation failed: {e}")
```

## Troubleshooting

### Credentials Not Found

```bash
# Verify credentials path
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Set explicitly
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/key.json"
```

### FFprobe Not Installed

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify
which ffprobe
ffprobe -version
```

### Timing Data Missing

If word timings are empty:

1. Verify `enable_timepointing` is set in AudioConfig
2. Check that the voice supports timepoints (most Neural voices do)
3. Enable debug logging to see API response

## Next Steps

Phase 1 complete! Next phases:

- [ ] **Phase 2**: Frame Generation - Create video frames with text animation
- [ ] **Phase 3**: Video Composition - Combine frames + audio with FFmpeg
- [ ] **Phase 4**: R2 Upload - Upload videos to Cloudflare R2
- [ ] **Phase 5**: Database - Save metadata to NeonDB

## References

- [Google Cloud TTS Documentation](https://cloud.google.com/text-to-speech/docs)
- [SSML Reference](https://cloud.google.com/text-to-speech/docs/ssml)
- [Supported Voices](https://cloud.google.com/text-to-speech/docs/voices)
- [Pricing](https://cloud.google.com/text-to-speech/pricing)
