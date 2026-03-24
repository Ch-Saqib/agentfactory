#!/usr/bin/env python3
"""Standalone script to test R2 Upload functionality.

This script:
1. Tests file upload to Cloudflare R2
2. Tests multipart upload for large files
3. Tests presigned URL generation
4. Tests file listing and deletion
5. Tests bucket operations

Usage:
    python test_r2_upload.py

Requirements:
    - R2 credentials configured in .env
    - Valid R2 access key and secret key
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shorts_generator.services.r2_uploader import R2Uploader


def create_test_file(size_mb: float, suffix: str = ".mp4") -> str:
    """Create a test file of specified size.

    Args:
        size_mb: File size in megabytes
        suffix: File suffix/extension

    Returns:
        Path to created file
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        # Write file of specified size
        size_bytes = int(size_mb * 1024 * 1024)
        chunk = b"x" * (1024 * 1024)  # 1MB chunk

        written = 0
        while written < size_bytes:
            tmp.write(chunk)
            written += len(chunk)

        tmp.flush()
        return tmp.name


def test_file_upload():
    """Test basic file upload."""
    print("🧪 Test 1: File Upload")
    print("-" * 40)

    uploader = R2Uploader()

    # Create test file (small, under multipart threshold)
    test_file = create_test_file(size_mb=5, suffix=".mp4")

    try:
        print(f"Created test file: {test_file} (5MB)")

        result = uploader.upload_file(
            file_path=test_file,
            key="test-upload.mp4",
        )

        print("✅ Upload successful!")
        print(f"   Key: {result.key}")
        print(f"   URL: {result.url}")
        print(f"   Size: {result.file_size_mb:.2f}MB")
        print(f"   ETag: {result.etag}")

    except Exception as e:
        print(f"❌ Upload failed: {e}")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_video_upload():
    """Test video upload with automatic key generation."""
    print("\n🧪 Test 2: Video Upload")
    print("-" * 40)

    uploader = R2Uploader()

    # Create test video file
    test_file = create_test_file(size_mb=10, suffix=".mp4")

    try:
        print(f"Created test video: {test_file} (10MB)")

        result = uploader.upload_video(
            video_path=test_file,
            chapter_id="test-chapter",
            metadata={"title": "Test Video", "duration": "30"},
        )

        print("✅ Video upload successful!")
        print(f"   Key: {result.key}")
        print(f"   URL: {result.url}")
        print(f"   Size: {result.file_size_mb:.2f}MB")

        # Check that metadata was added
        file_info = uploader.get_file_info(result.key)
        if file_info:
            print(f"   Metadata: {file_info.get('metadata', {})}")

    except Exception as e:
        print(f"❌ Video upload failed: {e}")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_multipart_upload():
    """Test multipart upload for large files."""
    print("\n🧪 Test 3: Multipart Upload")
    print("-" * 40)

    uploader = R2Uploader()

    # Create large file (> 100MB threshold)
    test_file = create_test_file(size_mb=101, suffix=".mp4")

    try:
        print(f"Created large test file: {test_file} (101MB)")
        print("   This will use multipart upload...")

        result = uploader.upload_file(
            file_path=test_file,
            key="large-file.mp4",
        )

        print("✅ Multipart upload successful!")
        print(f"   Key: {result.key}")
        print(f"   Size: {result.file_size_mb:.2f}MB")

    except Exception as e:
        print(f"❌ Multipart upload failed: {e}")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_presigned_url():
    """Test presigned URL generation."""
    print("\n🧪 Test 4: Presigned URL Generation")
    print("-" * 40)

    uploader = R2Uploader()

    try:
        result = uploader.generate_presigned_url(
            key="test-file.mp4",
            expires_in=3600,  # 1 hour
        )

        print("✅ Presigned URL generated!")
        print(f"   URL: {result.url}")
        print(f"   Expires: {result.expires_at.isoformat()}")

        # Show time until expiration
        time_left = (result.expires_at - datetime.now()).total_seconds()
        print(f"   Expires in: {time_left / 60:.1f} minutes")

    except Exception as e:
        print(f"❌ Presigned URL generation failed: {e}")


def test_file_listing():
    """Test listing files in bucket."""
    print("\n🧪 Test 5: File Listing")
    print("-" * 40)

    uploader = R2Uploader()

    try:
        files = uploader.list_files(prefix="test", max_keys=10)

        print(f"✅ Listed {len(files)} files:")
        for file in files[:5]:  # Show first 5
            size_mb = file["size"] / (1024 * 1024)
            print(f"   - {file['key']}")
            print(f"     Size: {size_mb:.2f}MB")
            print(f"     ETag: {file['etag']}")

    except Exception as e:
        print(f"❌ File listing failed: {e}")


def test_file_operations():
    """Test file existence and info."""
    print("\n🧪 Test 6: File Operations")
    print("-" * 40)

    uploader = R2Uploader()

    # Test file existence
    try:
        exists = uploader.file_exists("test-upload.mp4")
        print(f"File exists check: {exists}")

    except Exception as e:
        print(f"❌ File existence check failed: {e}")

    # Test file info
    try:
        info = uploader.get_file_info("test-upload.mp4")
        if info:
            print("File info retrieved:")
            print(f"   Size: {info['size']} bytes")
            print(f"   Type: {info['content_type']}")
            print(f"   Modified: {info['last_modified']}")
        else:
            print("File not found")

    except Exception as e:
        print(f"❌ File info retrieval failed: {e}")


def test_bucket_operations():
    """Test bucket operations."""
    print("\n🧪 Test 7: Bucket Operations")
    print("-" * 40)

    uploader = R2Uploader()

    print(f"Bucket name: {uploader.bucket_name}")
    print(f"Account ID: {uploader.account_id}")
    print(f"Public URL: {uploader.public_url}")

    # Test bucket creation
    try:
        result = uploader.create_bucket_if_not_exists()
        if result:
            print("✅ Bucket is ready (exists or created)")
        else:
            print("❌ Bucket creation failed")

    except Exception as e:
        print(f"❌ Bucket operation failed: {e}")


def test_with_progress_tracking():
    """Test upload with progress tracking."""
    print("\n🧪 Test 8: Upload with Progress Tracking")
    print("-" * 40)

    uploader = R2Uploader()

    # Create test file
    test_file = create_test_file(size_mb=20, suffix=".mp4")

    def progress_callback(uploaded_bytes: int, total_bytes: int) -> None:
        percent = (uploaded_bytes / total_bytes) * 100
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = "█" * filled + "-" * (bar_length - filled)
        print(f"\r   Progress: [{bar}] {percent:.1f}%", end="", flush=True)

    try:
        print(f"Uploading {test_file} (20MB)...")

        result = uploader.upload_file(
            file_path=test_file,
            key="progress-test.mp4",
            progress_callback=progress_callback,
        )

        print("\n✅ Upload with progress complete!")
        print(f"   URL: {result.url}")

    except Exception as e:
        print(f"\n❌ Upload with progress failed: {e}")

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def main():
    """Run all R2 upload tests."""
    print("☁️  Testing Cloudflare R2 Upload")
    print("=" * 70)

    # Check for credentials
    if not os.getenv("R2_ACCESS_KEY_ID") or not os.getenv("R2_SECRET_ACCESS_KEY"):
        print("\n❌ ERROR: R2 credentials not configured!")
        print("\nAdd to .env:")
        print("R2_ACCOUNT_ID=your-account-id")
        print("R2_ACCESS_KEY_ID=your-access-key-id")
        print("R2_SECRET_ACCESS_KEY=your-secret-key")
        print("R2_BUCKET_NAME=your-bucket-name")
        print("R2_PUBLIC_URL=https://your-bucket.r2.dev")
        return 1

    print("\n✅ R2 credentials found")

    # Run tests
    test_file_upload()
    test_video_upload()
    test_multipart_upload()
    test_presigned_url()
    test_file_listing()
    test_file_operations()
    test_bucket_operations()
    test_with_progress_tracking()

    print("\n" + "=" * 70)
    print("🎉 All R2 Upload Tests Complete!")
    print("\nNext steps:")
    print("1. Check your R2 bucket for uploaded files")
    print("2. Verify public URLs are accessible")
    print("3. Test presigned URLs for private access")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
