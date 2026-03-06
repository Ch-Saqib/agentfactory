#!/usr/bin/env python3
"""Standalone script to test Frame Generation.

This script:
1. Generates sample frames with text animation
2. Tests word-by-word timing synchronization
3. Creates title, content, and outro frames
4. Saves frames to output directory

Usage:
    python test_frame_generation.py

Requirements:
    - Google Cloud credentials (for TTS)
    - PIL/Pillow for image generation
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shorts_generator.services.frame_generator import FrameGenerator
from shorts_generator.services.google_tts_audio import GoogleCloudTTSGenerator


def test_frame_generation():
    """Test frame generation without TTS."""
    print("🎬 Testing Frame Generation")
    print("=" * 70)

    # Create generator
    generator = FrameGenerator()

    # Create output directory
    output_dir = Path(__file__).parent / "frame_test_output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n📁 Output directory: {output_dir}")
    print(f"   Frame size: {generator.spec.width}x{generator.spec.height}")
    print(f"   FPS: {generator.spec.fps}")

    # Test 1: Title frames
    print("\n🎬 Test 1: Title Frames")
    print("-" * 40)

    title_dir = output_dir / "title"
    title_dir.mkdir(exist_ok=True)

    title_frames = generator.generate_title_frames(
        title="The Seven Principles of Agent Work",
        duration=3.0,
        output_dir=str(title_dir),
    )

    print(f"✅ Generated {len(title_frames)} title frames")
    print(f"   Preview: {title_frames[0]}")

    # Test 2: Content frames (word sync with mock timing)
    print("\n🎬 Test 2: Content Frames (Word Sync)")
    print("-" * 40)

    from shorts_generator.services.google_tts_audio import WordTiming

    # Create mock word timings
    word_timings = [
        WordTiming("First", 0.0, 0.3),
        WordTiming("Bash", 0.3, 0.6),
        WordTiming("is", 0.6, 0.75),
        WordTiming("the", 0.75, 0.9),
        WordTiming("Key", 0.9, 1.2),
        WordTiming("Second", 1.2, 1.6),
        WordTiming("Code", 1.6, 1.85),
        WordTiming("as", 1.85, 2.0),
        WordTiming("Interface", 2.0, 2.5),
        WordTiming("Third", 2.5, 2.8),
        WordTiming("Verification", 2.8, 3.4),
        WordTiming("is", 3.4, 3.55),
        WordTiming("Core", 3.55, 3.8),
    ]

    content_dir = output_dir / "content"
    content_dir.mkdir(exist_ok=True)

    content_frames = generator.generate_content_frames_word_sync(
        content=" ".join([w.word for w in word_timings]),
        word_timings=word_timings,
        start_time=0.0,
        end_time=5.0,
        output_dir=str(content_dir),
    )

    print(f"✅ Generated {len(content_frames)} content frames")
    print(f"   Preview: {content_frames[0]}")

    # Test 3: Outro frames
    print("\n🎬 Test 3: Outro Frames")
    print("-" * 40)

    outro_dir = output_dir / "outro"
    outro_dir.mkdir(exist_ok=True)

    outro_frames = generator.generate_outro_frames(
        cta_text="Continue reading at agentfactory.panaversity.org",
        duration=3.0,
        output_dir=str(outro_dir),
    )

    print(f"✅ Generated {len(outro_frames)} outro frames")
    print(f"   Preview: {outro_frames[0]}")

    # Summary
    total_frames = len(title_frames) + len(content_frames) + len(outro_frames)
    total_duration = total_frames / generator.spec.fps

    print(f"\n{'='*70}")
    print("🎉 Frame Generation Complete!")
    print(f"   Total frames: {total_frames}")
    print(f"   Total duration: {total_duration:.2f}s")
    print(f"   Output directory: {output_dir}")
    print("\nNext steps:")
    print(f"   1. Review sample frames in {output_dir}")
    print("   2. Check text rendering quality")
    print("   3. Verify fade effects in frame sequence")
    print(f"{'='*70}\n")


async def test_full_pipeline():
    """Test full pipeline with Google Cloud TTS and frame generation."""
    print("🎬 Testing Full Pipeline: TTS + Frame Generation")
    print("=" * 70)

    # Check for credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   Skipping full pipeline test.")
        return

    # Create generators
    tts_gen = GoogleCloudTTSGenerator(voice_preset="narration_male")
    frame_gen = FrameGenerator()

    # Create output directory
    output_dir = Path(__file__).parent / "pipeline_test_output"
    output_dir.mkdir(exist_ok=True)

    # Test content
    test_text = (
        "The Seven Principles of Agent Work guide everything we do. "
        "First, Bash is the Key — use command line tools for efficiency. "
        "Second, Code as Universal Interface — express work as code, not prose."
    )

    print(f"\n📝 Test text: \"{test_text}\"")
    print("\n🎤 Step 1: Generating audio with Google Cloud TTS...")

    try:
        # Generate audio with timing
        tts_result = tts_gen.generate(test_text)

        print(f"✅ Audio generated: {tts_result.duration_seconds:.2f}s")
        print(f"   Word timings: {len(tts_result.word_timings)}")

        # Save timing data
        timing_path = output_dir / "timing.json"
        tts_result.save_timing_json(str(timing_path))
        print(f"   Timing data: {timing_path}")

    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        return

    print("\n🎬 Step 2: Generating frames with word sync...")

    try:
        # Generate frames
        frame_result = frame_gen.generate_video_frames(
            title="Seven Principles of Agent Work",
            content=test_text,
            tts_result=tts_result,
            title_duration=2.0,
            outro_duration=2.0,
            output_dir=str(output_dir / "frames"),
            use_word_sync=True,
        )

        print(f"✅ Frames generated: {frame_result.frame_count}")
        print(f"   Total duration: {frame_result.total_duration:.2f}s")
        print(f"   Output directory: {frame_result.output_dir}")

        # Sample frame paths
        print("\n📸 Sample frames:")
        print(f"   First frame: {frame_result.frame_paths[0]}")
        print(f"   Middle frame: {frame_result.frame_paths[frame_result.frame_count // 2]}")
        print(f"   Last frame: {frame_result.frame_paths[-1]}")

    except Exception as e:
        print(f"❌ Frame generation failed: {e}")
        return

    print(f"\n{'='*70}")
    print("🎉 Full Pipeline Test Complete!")
    print("\nGenerated files:")
    print(f"   1. Audio: {tts_result.audio_path}")
    print(f"   2. Timing: {timing_path}")
    print(f"   3. Frames: {output_dir}/frames/")
    print("\nTo view frames, open them in an image viewer or:")
    ffmpeg_cmd = (
        f"ffmpeg -framerate 30 -i {output_dir}/frames/frame_%05d.png "
        f"-c:v libx264 -pix_fmt yuv420p output.mp4"
    )
    print(f"   {ffmpeg_cmd}")
    print(f"{'='*70}\n")


def main():
    """Run tests."""
    # Test 1: Frame generation only (fast, no credentials needed)
    test_frame_generation()

    # Test 2: Full pipeline with TTS (requires credentials)
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        asyncio.run(test_full_pipeline())
    else:
        print("\n⚠️  Skipping full pipeline test (no Google Cloud credentials)")
        print("   Set GOOGLE_APPLICATION_CREDENTIALS to test the full pipeline.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
