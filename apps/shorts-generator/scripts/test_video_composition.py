#!/usr/bin/env python3
"""Standalone script to test Video Composition.

This script:
1. Creates sample frames and audio
2. Composes them into a video using FFmpeg
3. Generates thumbnails
4. Verifies the output

Usage:
    python test_video_composition.py

Requirements:
    - FFmpeg installed
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PIL import Image, ImageDraw

from shorts_generator.services.frame_generator import FrameGenerator
from shorts_generator.services.google_tts_audio import GoogleCloudTTSGenerator
from shorts_generator.services.video_composer import VideoComposer


def create_sample_frames(output_dir: str, num_frames: int = 30):
    """Create sample video frames.

    Args:
        output_dir: Directory to save frames
        num_frames: Number of frames to generate
    """
    print("🎬 Creating sample frames...")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create frames with changing text
    for i in range(num_frames):
        img = Image.new("RGB", (1080, 1920), color=(26, 26, 46))
        draw = ImageDraw.Draw(img)

        # Add text
        text = f"Frame {i + 1}/{num_frames}"
        draw.text((540, 960), text, fill=(255, 255, 255), anchor="mm")

        # Save frame
        frame_path = output_path / f"frame_{i:05d}.png"
        img.save(frame_path)

    print(f"✅ Created {num_frames} frames in {output_dir}")


def create_sample_audio(output_path: str):
    """Create a sample audio file.

    Args:
        output_path: Path to save audio file

    Returns:
        Path to audio file
    """
    print("🎤 Creating sample audio...")

    # Create a minimal WAV file
    import wave

    audio_path = Path(output_path)
    with wave.open(str(audio_path), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(24000)  # 24kHz

        # 1 second of silence
        num_frames = 24000
        wav_file.writeframes(b"\x00\x00" * num_frames)

    print(f"✅ Created audio file: {audio_path}")
    return str(audio_path)


async def test_video_composition():
    """Test video composition with sample data."""
    print("🎬 Testing Video Composition")
    print("=" * 70)

    # Check FFmpeg availability
    print("\n🔍 Checking FFmpeg availability...")
    try:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-version",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.wait()

        if process.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg is not available")
            return 1
    except FileNotFoundError:
        print("❌ FFmpeg is not installed")
        print("   Install with: apt-get install ffmpeg")
        return 1

    # Create output directory
    output_dir = Path(__file__).parent / "video_composition_test_output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n📁 Output directory: {output_dir}")

    # Test 1: Basic composition
    print("\n" + "=" * 70)
    print("🧪 Test 1: Basic Video Composition")
    print("-" * 40)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample data
        frames_dir = Path(tmpdir) / "frames"
        create_sample_frames(str(frames_dir), num_frames=30)

        audio_path = Path(tmpdir) / "audio.wav"
        create_sample_audio(str(audio_path))

        # Compose video
        video_path = output_dir / "test1_basic.mp4"

        composer = VideoComposer()

        try:
            result = await composer.compose(
                frames_dir=str(frames_dir),
                audio_path=str(audio_path),
                output_path=str(video_path),
                fps=30,
            )

            print("✅ Video composed successfully!")
            print(f"   Path: {result.video_path}")
            print(f"   Duration: {result.duration_seconds:.2f}s")
            print(f"   Size: {result.file_size_mb:.2f}MB")
            print(f"   Resolution: {result.width}x{result.height}")
            print(f"   FPS: {result.fps}")

        except Exception as e:
            print(f"❌ Composition failed: {e}")
            return 1

    # Test 2: Composition with progress callback
    print("\n" + "=" * 70)
    print("🧪 Test 2: Composition with Progress Callback")
    print("-" * 40)

    with tempfile.TemporaryDirectory() as tmpdir:
        frames_dir = Path(tmpdir) / "frames"
        create_sample_frames(str(frames_dir), num_frames=90)  # 3 seconds

        audio_path = Path(tmpdir) / "audio.wav"
        create_sample_audio(str(audio_path))

        video_path = output_dir / "test2_with_progress.mp4"

        progress_updates = []

        def progress_callback(progress: float) -> None:
            progress_updates.append(progress)
            percent = int(progress * 100)
            print(f"   Progress: {percent}%\r", end="", flush=True)

        try:
            print()  # New line before progress
            result = await composer.compose(
                frames_dir=str(frames_dir),
                audio_path=str(audio_path),
                output_path=str(video_path),
                fps=30,
                progress_callback=progress_callback,
            )

            print()  # New line after progress
            print("✅ Video composed with progress tracking!")
            print(f"   Progress updates: {len(progress_updates)}")

        except Exception as e:
            print(f"\n❌ Composition failed: {e}")
            return 1

    # Test 3: Generate thumbnail
    print("\n" + "=" * 70)
    print("🧪 Test 3: Thumbnail Generation")
    print("-" * 40)

    try:
        thumbnail_path = await composer.generate_thumbnail(
            video_path=str(output_dir / "test1_basic.mp4"),
            timestamp=0.5,
            width=320,
        )

        print(f"✅ Thumbnail generated: {thumbnail_path}")

    except Exception as e:
        print(f"❌ Thumbnail generation failed: {e}")

    # Test 4: Video verification
    print("\n" + "=" * 70)
    print("🧪 Test 4: Video Verification")
    print("-" * 40)

    try:
        verification = await composer.verify_video(
            video_path=str(output_dir / "test1_basic.mp4"),
            expected_duration=1.0,
            tolerance=0.5,
        )

        print(f"   Exists: {verification['exists']}")
        print(f"   Readable: {verification['readable']}")
        print(f"   Has Video: {verification['has_video']}")
        print(f"   Duration Match: {verification['duration_match']}")

        if verification.get("width"):
            print(f"   Resolution: {verification['width']}x{verification['height']}")
            print(f"   FPS: {verification['fps']}")
            print(f"   Duration: {verification['duration']:.2f}s")

    except Exception as e:
        print(f"❌ Verification failed: {e}")

    # Test 5: Create preview
    print("\n" + "=" * 70)
    print("🧪 Test 5: Preview Creation")
    print("-" * 40)

    try:
        preview_path = await composer.create_preview(
            video_path=str(output_dir / "test1_basic.mp4"),
            duration=1.0,
            start_time=0.0,
        )

        print(f"✅ Preview created: {preview_path}")

    except Exception as e:
        print(f"❌ Preview creation failed: {e}")

    print("\n" + "=" * 70)
    print("🎉 All Video Composition Tests Complete!")
    print(f"\nGenerated files in {output_dir}:")
    for file in output_dir.iterdir():
        if file.is_file():
            size = file.stat().st_size / 1024  # KB
            print(f"  - {file.name} ({size:.1f}KB)")
    print("=" * 70 + "\n")

    return 0


async def test_full_pipeline():
    """Test full pipeline: TTS + Frames + Video Composition."""
    print("🎬 Testing Full Pipeline: TTS + Frames + Composition")
    print("=" * 70)

    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("\n⚠️  Skipping full pipeline (no Google Cloud credentials)")
        return 0

    # Create generators
    tts_gen = GoogleCloudTTSGenerator()
    frame_gen = FrameGenerator()
    video_comp = VideoComposer()

    output_dir = Path(__file__).parent / "full_pipeline_output"
    output_dir.mkdir(exist_ok=True)

    # Test content
    test_text = "This is a test of the full video generation pipeline."

    print(f"\n📝 Text: \"{test_text}\"")

    # Generate audio
    print("\n🎤 Step 1: Generating audio...")
    try:
        tts_result = tts_gen.generate(test_text)
        print(f"✅ Audio: {tts_result.duration_seconds:.2f}s, {len(tts_result.word_timings)} words")
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        return 1

    # Generate frames
    print("\n🎬 Step 2: Generating frames...")
    try:
        frame_result = frame_gen.generate_video_frames(
            title="Full Pipeline Test",
            content=test_text,
            tts_result=tts_result,
            title_duration=1.0,
            outro_duration=1.0,
            output_dir=str(output_dir / "frames"),
            use_word_sync=True,
        )
        print(f"✅ Frames: {frame_result.frame_count} frames, {frame_result.total_duration:.2f}s")
    except Exception as e:
        print(f"❌ Frame generation failed: {e}")
        return 1

    # Compose video
    print("\n🎥 Step 3: Composing video...")
    video_path = str(output_dir / "full_pipeline_video.mp4")

    try:
        video_result = await video_comp.compose(
            frames_dir=frame_result.output_dir,
            audio_path=tts_result.audio_path,
            output_path=video_path,
        )

        print(f"✅ Video: {video_result.video_path}")
        print(f"   Duration: {video_result.duration_seconds:.2f}s")
        print(f"   Size: {video_result.file_size_mb:.2f}MB")

    except Exception as e:
        print(f"❌ Video composition failed: {e}")
        return 1

    # Generate thumbnail
    print("\n🖼️  Step 4: Generating thumbnail...")
    try:
        thumbnail_path = await video_comp.generate_thumbnail(
            video_path=video_path,
            width=320,
        )
        print(f"✅ Thumbnail: {thumbnail_path}")
    except Exception as e:
        print(f"⚠️  Thumbnail generation failed: {e}")

    print("\n" + "=" * 70)
    print("🎉 Full Pipeline Complete!")
    print(f"\nOutput directory: {output_dir}")
    print("\nGenerated files:")
    print(f"  1. Audio: {tts_result.audio_path}")
    print(f"  2. Frames: {frame_result.output_dir}/")
    print(f"  3. Video: {video_result.video_path}")
    if video_result.thumbnail_path:
        print(f"  4. Thumbnail: {video_result.thumbnail_path}")
    print("=" * 70 + "\n")

    return 0


def main():
    """Run tests."""
    # Test video composition (requires FFmpeg)
    result = asyncio.run(test_video_composition())
    if result != 0:
        return result

    # Test full pipeline (requires FFmpeg + Google Cloud credentials)
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        result = asyncio.run(test_full_pipeline())

    return result


if __name__ == "__main__":
    sys.exit(main())
