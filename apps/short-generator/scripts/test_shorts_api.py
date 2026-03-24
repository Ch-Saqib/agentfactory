"""Manual Test Script for Shorts Generation API.

This script tests the shorts generation API endpoints with a real server.

Usage:
    # Start the server first:
    uvicorn shorts_generator.main:app --reload

    # Then run this script:
    python scripts/test_shorts_api.py

Requirements:
    - Server running on http://localhost:8000
    - Google Cloud TTS credentials configured
    - R2 storage configured
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


def test_health_check() -> bool:
    """Test health check endpoint."""
    print_test("Health Check")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/shorts/health", timeout=5)
        response.raise_for_status()

        data = response.json()
        print_success(f"Health check passed: {data['status']}")

        # Print component status
        for component, status_val in data.get("components", {}).items():
            healthy = ("healthy", "configured", "available")
            status_color = Colors.OKGREEN if status_val in healthy else Colors.FAIL
            print(f"  {component}: {status_color}{status_val}{Colors.ENDC}")

        return data["status"] in ("healthy", "degraded")

    except requests.exceptions.RequestException as e:
        print_error(f"Health check failed: {e}")
        return False


def test_generate_from_markdown() -> str | None:
    """Test video generation from markdown."""
    print_test("Generate Video from Markdown")

    request_data = {
        "markdown_content": """# Test Chapter: Introduction to AI Agents

This is a test chapter about AI agents and how they work.

## What are AI Agents?

AI agents are autonomous systems that can perceive, reason, and act in their environment.

## Key Concepts

- **Perception**: Understanding the environment
- **Reasoning**: Making decisions based on available information
- **Action**: Executing decisions in the real world

## Conclusion

AI agents are transforming how we interact with technology.
""",
        "chapter_id": "test-chapter-api-001",
        "chapter_title": "Test Chapter: Introduction to AI Agents",
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
        print_info(f"Message: {data.get('message')}")

        return job_id

    except requests.exceptions.RequestException as e:
        print_error(f"Generation request failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            print_error(f"Response: {e.response.text}")
        return None


def test_job_status(job_id: str) -> bool:
    """Test getting job status."""
    print_test(f"Job Status: {job_id}")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/shorts/jobs/{job_id}",
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        print_success(f"Job status: {data['status']}")
        print_info(f"Progress: {data['progress']}%")

        if data.get("error_message"):
            print_warning(f"Error: {data['error_message']}")

        if data.get("result"):
            print_info("Result available:")
            for key, value in data["result"].items():
                print(f"  {key}: {value}")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Job status request failed: {e}")
        return False


def test_wait_for_completion(job_id: str, max_wait_seconds: int = 300) -> bool:
    """Wait for job completion with progress updates."""
    print_test(f"Waiting for job completion: {job_id}")

    start_time = time.time()
    last_progress = -1

    while time.time() - start_time < max_wait_seconds:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/shorts/jobs/{job_id}",
                timeout=5,
            )
            response.raise_for_status()

            data = response.json()
            progress = data.get("progress", 0)
            status_val = data.get("status", "")

            # Print progress if changed
            if progress != last_progress:
                print_info(f"Progress: {progress}% | Status: {status_val}")
                last_progress = progress

            if status_val in ("completed", "failed"):
                if status_val == "completed":
                    print_success("Job completed successfully!")
                    if data.get("result"):
                        print_info("Result:")
                        for key, value in data["result"].items():
                            print(f"  {key}: {value}")
                else:
                    print_error(f"Job failed: {data.get('error_message')}")
                return status_val == "completed"

            time.sleep(2)

        except requests.exceptions.RequestException:
            print_warning("Status check failed, retrying...")
            time.sleep(2)

    print_warning(f"Job timed out after {max_wait_seconds} seconds")
    return False


def test_list_videos() -> bool:
    """Test listing videos."""
    print_test("List Videos")

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
                print(f"    Chapter ID: {video.get('chapter_id')}")
                print(f"    Duration: {video.get('duration_seconds')}s")
                if video.get("views"):
                    print(f"    Views: {video.get('views')}")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"List videos failed: {e}")
        return False


def test_get_video_by_chapter(chapter_id: str) -> bool:
    """Test getting video by chapter ID."""
    print_test(f"Get Video by Chapter: {chapter_id}")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/shorts/videos/by-chapter/{chapter_id}",
            timeout=5,
        )

        if response.status_code == 404:
            print_warning("Video not found for this chapter")
            return False

        response.raise_for_status()
        data = response.json()

        print_success(f"Found video: {data.get('chapter_title')}")
        print_info(f"Video URL: {data.get('video_url')}")
        print_info(f"Thumbnail URL: {data.get('thumbnail_url')}")
        print_info(f"Duration: {data.get('duration_seconds')}s")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Get video by chapter failed: {e}")
        return False


def test_videos_for_page() -> bool:
    """Test getting videos for shorts page."""
    print_test("Get Videos for Shorts Page")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/shorts/videos/for-page",
            params={"limit": 20},
            timeout=5,
        )
        response.raise_for_status()

        data = response.json()
        print_success(f"Retrieved {len(data)} videos for shorts page")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"Get videos for page failed: {e}")
        return False


def run_all_tests() -> None:
    """Run all API tests."""
    print_header("Shorts Generation API Test Suite")

    print_info(f"API Base URL: {BASE_URL}")
    print_info("Make sure the server is running before continuing...")

    input("\nPress Enter to start tests...")

    results = []

    # Test 1: Health check
    results.append(("Health Check", test_health_check()))

    if not results[-1][1]:
        print_error("Server health check failed. Please start the server.")
        return

    # Test 2: Generate video from markdown
    job_id = test_generate_from_markdown()
    generation_success = job_id is not None
    results.append(("Generate from Markdown", generation_success))

    # Test 3: Wait for completion (if job was created)
    if job_id:
        print_info("\nWaiting for generation to complete...")
        completion_success = test_wait_for_completion(job_id, max_wait_seconds=600)  # 10 minutes
        results.append(("Generation Completion", completion_success))

        # Test 4: Get video by chapter
        if completion_success:
            chapter_result = test_get_video_by_chapter("test-chapter-api-001")
            results.append(("Get Video by Chapter", chapter_result))

    # Test 5: List videos
    results.append(("List Videos", test_list_videos()))

    # Test 6: Videos for page
    results.append(("Videos for Page", test_videos_for_page()))

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
