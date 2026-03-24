#!/usr/bin/env python3
"""Standalone script to test Google Cloud TTS word-level timing accuracy.

This script:
1. Generates audio from sample text
2. Extracts word-level timing data
3. Saves audio file + timing JSON
4. Prints timing report

Usage:
    python test_timing_accuracy.py

Requirements:
    - GOOGLE_APPLICATION_CREDENTIALS environment variable set
    - ffprobe installed (for audio duration detection)
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shorts_generator.services.google_tts_audio import GoogleCloudTTSGenerator


def print_timing_report(result):
    """Print formatted timing report."""
    print(f"\n{'='*70}")
    print("GOOGLE CLOUD TTS TIMING REPORT")
    print(f"{'='*70}")
    print(f"Voice:              {result.voice_used}")
    print(f"Encoding:           {result.encoding}")
    print(f"Sample Rate:        {result.sample_rate} Hz")
    print(f"Duration:           {result.duration_seconds:.3f} seconds")
    print(f"Word Count:         {len(result.word_timings)}")
    print(f"Average Word Time:  {result.duration_seconds / max(len(result.word_timings), 1):.3f}s")
    print(f"{'='*70}")

    if result.word_timings:
        print(f"\n{'Word':<20} {'Start':<12} {'End':<12} {'Duration':<10}")
        print("-" * 70)

        for i, timing in enumerate(result.word_timings):
            duration = timing.end_time - timing.start_time
            print(
                f"{timing.word:<20} {timing.start_time:<12.3f} "
                f"{timing.end_time:<12.3f} {duration:<10.3f}s"
            )

            # Highlight any anomalies
            if duration > 1.0:
                print("  ⚠️  Long duration detected!")
            if duration < 0.05:
                print("  ⚠️  Very short duration detected!")

        print(f"\n{'='*70}")

        # Verify timing consistency
        print("\nTIMING CONSISTENCY CHECK:")
        print("-" * 40)

        issues = []

        # Check for gaps between words
        for i in range(1, len(result.word_timings)):
            prev = result.word_timings[i - 1]
            curr = result.word_timings[i]
            gap = curr.start_time - prev.end_time

            if gap < 0:
                issues.append(
                    f"Overlap detected: '{prev.word}' and '{curr.word}' "
                    f"overlap by {abs(gap):.3f}s"
                )
            elif gap > 0.5:
                issues.append(
                    f"Large gap: {gap:.3f}s between '{prev.word}' and '{curr.word}'"
                )

        # Check total duration consistency
        if result.word_timings:
            last_end = result.word_timings[-1].end_time
            duration_diff = abs(last_end - result.duration_seconds)

            if duration_diff > 2.0:
                issues.append(
                    f"Duration mismatch: Last word ends at {last_end:.3f}s "
                    f"but total duration is {result.duration_seconds:.3f}s"
                )

        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ No timing issues detected!")

        print(f"\n{'='*70}")


def test_sample_texts():
    """Test with various sample texts."""
    return [
        {
            "name": "Simple Sentence",
            "text": "Hello world. This is a test.",
        },
        {
            "name": "Technical Content",
            "text": (
                "The Seven Principles of Agent Work guide everything we do. "
                "First, Bash is the Key — use command line tools for efficiency."
            ),
        },
        {
            "name": "Punctuation Test",
            "text": "Hello! How are you? I'm doing great, thanks.",
        },
        {
            "name": "Numbers and Symbols",
            "text": "There are 7 principles. The cost is $0.006 per video.",
        },
    ]


async def main():
    """Run timing accuracy test."""
    # Check for credentials
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS environment variable not set!")
        print("\nTo set up Google Cloud TTS:")
        print("1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts")
        print("2. Create a service account with 'Cloud Text-to-Speech API User' role")
        print("3. Download the JSON key file")
        print("4. Export: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        return 1

    print("🎤 Testing Google Cloud TTS Word-Level Timing Accuracy")
    print("=" * 70)

    # Create generator
    generator = GoogleCloudTTSGenerator(voice_preset="narration_male")

    # Create output directory
    output_dir = Path(__file__).parent / "timing_test_output"
    output_dir.mkdir(exist_ok=True)

    # Test each sample
    for i, sample in enumerate(test_sample_texts()):
        print(f"\n📝 Test {i+1}: {sample['name']}")
        print(f"   Text: \"{sample['text']}\"")

        try:
            # Generate audio
            result = generator.generate(
                sample['text'],
                output_path=str(output_dir / f"test_{i+1}.mp3")
            )

            # Save timing JSON
            timing_path = output_dir / f"test_{i+1}_timing.json"
            result.save_timing_json(str(timing_path))

            # Print report
            print_timing_report(result)

            print(f"\n✅ Audio saved to: {result.audio_path}")
            print(f"✅ Timing data saved to: {timing_path}")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            continue

    print(f"\n{'='*70}")
    print(f"🎉 All tests complete! Output saved to: {output_dir}")
    print("\nNext steps:")
    print("1. Play the audio files to verify quality")
    print("2. Check timing JSON files for word-level accuracy")
    print("3. Use timing data for word-by-word caption sync")
    print(f"{'='*70}\n")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
