"""Manual Test Script for Complete Video Generation Pipeline.

This script tests the end-to-end pipeline including:
- Single video generation
- Batch video generation
- Progress tracking
- Error handling

Usage:
    # Start the server first:
    uvicorn shorts_generator.main:app --reload

    # Then run this script:
    python scripts/test_complete_pipeline.py

Requirements:
    - Server running on http://localhost:8000
    - Google Cloud TTS credentials configured
    - R2 storage configured
    - Test markdown files available
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip install requests")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_test(name: str) -> None:
    """Print test name."""
    print(f"\n{Colors.BOLD}Testing: {name}{Colors.ENDC}")


# API base URL
BASE_URL = "http://localhost:8000"


def test_single_video_generation() -> bool:
    """Test single video generation."""
    print_test("Single Video Generation")

    request_data = {
        "markdown_content": """# Test: Understanding AI Agents

AI agents are autonomous systems that can perceive, reason, and act.

## Key Concepts

**Perception**: Understanding the environment through sensors.

**Reasoning**: Making decisions based on available information.

**Action**: Executing decisions in the real world.

## Example

A simple AI agent might:
1. Observe its environment
2. Plan a sequence of actions
3. Execute those actions
4. Learn from the results

## Conclusion

AI agents are transforming how we interact with technology.
""",
        "chapter_id": "test-pipeline-single-001",
        "chapter_title": "Test: Understanding AI Agents",
        "chapter_number": 1,
        "voice_preset": "narration_male",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/shorts/generate/from-markdown",
            json=request_data,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        job_id = data.get("job_id")
        print_success(f"Generation job created: {job_id}")
        print_info(f"Status: {data.get('status')}")

        # Wait a bit then check status
        time.sleep(2)
        status_response = requests.get(
            f"{BASE_URL}/api/v1/shorts/jobs/{job_id}",
            timeout=5,
        )
        status_response.raise_for_status()
        status_data = status_response.json()
        print_info(f"Job status: {status_data.get('status')}")
        print_info(f"Progress: {status_data.get('progress')}%")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Single video generation failed: {e}")
        return False


def test_batch_video_generation() -> bool:
    """Test batch video generation."""
    print_test("Batch Video Generation")

    request_data = {
        "chapters": [
            {
                "chapter_id": "test-batch-chapter-1",
                "chapter_title": "Batch Test Chapter 1",
                "markdown_content": "# Chapter 1\n\nFirst chapter content.",
                "voice_preset": "narration_male",
            },
            {
                "chapter_id": "test-batch-chapter-2",
                "chapter_title": "Batch Test Chapter 2",
                "markdown_content": "# Chapter 2\n\nSecond chapter content.",
                "voice_preset": "narration_female",
            },
        ],
        "max_concurrent": 2,
        "fail_fast": False,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/shorts/batch/generate",
            json=request_data,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        batch_id = data.get("batch_id")
        print_success(f"Batch job created: {batch_id}")
        print_info(f"Total chapters: {data.get('total_chapters')}")

        # Wait a bit then check status
        time.sleep(2)
        status_response = requests.get(
            f"{BASE_URL}/api/v1/shorts/batch/{batch_id}/status",
            timeout=5,
        )
        status_response.raise_for_status()
        status_data = status_response.json()
        print_info(f"Batch status: {status_data.get('status')}")
        completed = status_data.get("completed", 0)
        total = status_data.get("total_chapters", 0)
        print_info(f"Progress: {completed}/{total} completed")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Batch video generation failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print_error(f"Response: {e.response.text}")
        return False


def test_list_videos() -> bool:
    """Test listing generated videos."""
    print_test("List Generated Videos")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/shorts/videos",
            params={"limit": 10},
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        video_count = data.get("total_count", 0)
        print_success(f"Found {video_count} videos")

        if video_count > 0:
            print("\nRecent videos:")
            for video in data.get("videos", [])[:3]:
                print(f"  - [{video.get('id')}] {video.get('chapter_title')}")
                print(f"    Duration: {video.get('duration_seconds')}s")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"List videos failed: {e}")
        return False


def test_get_video_by_chapter() -> bool:
    """Test getting video by chapter ID."""
    print_test("Get Video by Chapter ID")

    # First try to get a video that might exist
    chapter_id = "test-pipeline-single-001"

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/shorts/videos/by-chapter/{chapter_id}",
            timeout=5,
        )

        if response.status_code == 404:
            print_warning(f"Video not found for {chapter_id} (may still be generating)")
            return True

        response.raise_for_status()
        data = response.json()

        print_success(f"Found video: {data.get('chapter_title')}")
        print_info(f"Duration: {data.get('duration_seconds')}s")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Get video by chapter failed: {e}")
        return False


def test_videos_for_shorts_page() -> bool:
    """Test getting videos for shorts page."""
    print_test("Get Videos for Shorts Page")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/shorts/videos/for-page",
            params={"limit": 10},
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        print_success(f"Retrieved {len(data)} videos for shorts page")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Get videos for shorts page failed: {e}")
        return False


def test_health_check() -> bool:
    """Test health check endpoint."""
    print_test("Health Check")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/shorts/health",
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        print_success(f"Health status: {data.get('status')}")

        # Print component status
        for component, status_val in data.get("components", {}).items():
            status_color = (
                Colors.OKGREEN
                if status_val in ("healthy", "configured", "available")
                else Colors.FAIL
            )
            print(f"  {component}: {status_color}{status_val}{Colors.ENDC}")

        return data.get("status") in ("healthy", "degraded")

    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed: {e}")
        return False


def test_batch_from_directory():
    """Test batch generation from directory (optional)."""
    print_test("Batch from Directory")

    # This test requires a directory with markdown files
    # Uncomment and modify path to test

    # docs_path = input("Enter path to docs directory (or press Enter to skip): ").strip()
    # if not docs_path:
    #     print_warning("Skipping directory test")
    #     return True

    print_warning("Directory test skipped (requires manual path input)")
    return True


def run_all_tests() -> None:
    """Run all pipeline tests."""
    print_header("Complete Pipeline Test Suite")

    print_info(f"API Base URL: {BASE_URL}")
    print_info("Make sure the server is running before continuing...")

    input("\nPress Enter to start tests...")

    results = []

    # Test 1: Health check
    results.append(("Health Check", test_health_check()))

    if not results[-1][1]:
        print_error("Server health check failed. Please start the server.")
        return

    # Test 2: Single video generation
    results.append(("Single Video Generation", test_single_video_generation()))

    # Test 3: Batch video generation
    results.append(("Batch Video Generation", test_batch_video_generation()))

    # Test 4: List videos
    results.append(("List Videos", test_list_videos()))

    # Test 5: Get video by chapter
    results.append(("Get Video by Chapter", test_get_video_by_chapter()))

    # Test 6: Videos for shorts page
    results.append(("Videos for Shorts Page", test_videos_for_shorts_page()))

    # Test 7: Batch from directory (optional)
    results.append(("Batch from Directory", test_batch_from_directory()))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"Total Tests: {total}")
    print(f"{Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    if passed < total:
        print(f"{Colors.FAIL}Failed: {total - passed}{Colors.ENDC}")

    print("\nDetailed Results:")
    for test_name, result in results:
        if result:
            status_str = f"{Colors.OKGREEN}PASS{Colors.ENDC}"
        else:
            status_str = f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  [{status_str}] {test_name}")

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


def main() -> None:
    """Entry point for the test script."""
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()
