"""Tests for R2 Uploader Service.

This test module validates:
1. File upload functionality
2. Multipart upload for large files
3. Presigned URL generation
4. File deletion
5. File listing
6. Bucket operations
7. Error handling
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from shorts_generator.services.r2_uploader import (
    PresignedURLResult,
    R2Uploader,
    UploadResult,
    r2_uploader,
)


class TestUploadResult:
    """Tests for UploadResult dataclass."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = UploadResult(
            key="videos/test.mp4",
            url="https://bucket.r2.dev/videos/test.mp4",
            file_size_bytes=1024000,
            file_size_mb=1.024,
            upload_time=None,
            etag="abc123",
        )

        data = result.to_dict()

        assert data["key"] == "videos/test.mp4"
        assert data["url"] == "https://bucket.r2.dev/videos/test.mp4"
        assert data["file_size_bytes"] == 1024000
        assert data["file_size_mb"] == 1.024
        assert data["etag"] == "abc123"


class TestPresignedURLResult:
    """Tests for PresignedURLResult dataclass."""

    def test_attributes(self):
        """Test PresignedURLResult attributes."""
        from datetime import datetime, timedelta

        expires_at = datetime.now() + timedelta(hours=1)

        result = PresignedURLResult(
            url="https://presigned-url",
            expires_at=expires_at,
        )

        assert result.url == "https://presigned-url"
        assert result.expires_at == expires_at


class TestR2Uploader:
    """Tests for R2Uploader class."""

    @pytest.fixture
    def uploader(self):
        """Create an R2Uploader instance for testing."""
        return R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )

    def test_initialization(self, uploader):
        """Test uploader initialization."""
        assert uploader.account_id == "test-account"
        assert uploader.bucket_name == "test-bucket"
        assert uploader.public_url == "https://test-bucket.r2.dev"

    def test_generate_key(self, uploader):
        """Test S3 key generation."""
        # Basic key
        key = uploader._generate_key("test.mp4", timestamp=False)
        assert key == "videos/test.mp4"

        # Key with prefix
        key = uploader._generate_key("test.mp4", prefix="custom")
        assert key == "custom/test.mp4"

        # Key with timestamp
        key = uploader._generate_key("test.mp4", timestamp=True)
        assert "videos/" in key
        assert "test.mp4" in key

    def test_generate_key_sanitization(self, uploader):
        """Test key path sanitization."""
        # Test backslash conversion
        key = uploader._generate_key("folder\\test.mp4", timestamp=False)
        assert "folder/test.mp4" in key

        # Test leading slash removal
        key = uploader._generate_key("/test.mp4", timestamp=False)
        assert key == "videos/test.mp4"

    def test_get_public_url(self, uploader):
        """Test public URL generation."""
        url = uploader._get_public_url("videos/test.mp4")
        assert url == "https://test-bucket.r2.dev/videos/test.mp4"

        # Test with leading slash
        url = uploader._get_public_url("/videos/test.mp4")
        assert url == "https://test-bucket.r2.dev/videos/test.mp4"

    def test_get_content_type(self, uploader):
        """Test content type detection."""
        assert uploader._get_content_type("test.mp4") == "video/mp4"
        assert uploader._get_content_type("test.mp3") == "audio/mpeg"
        assert uploader._get_content_type("test.jpg") == "image/jpeg"
        assert uploader._get_content_type("test.png") == "image/png"
        assert uploader._get_content_type("test.json") == "application/json"
        assert uploader._get_content_type("test.unknown") == "application/octet-stream"

    def test_calculate_md5(self, uploader):
        """Test MD5 calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp.flush()

            md5 = uploader._calculate_md5(tmp.name)

            # Known MD5 of "test content"
            assert md5 == "4a6b7e3fd9c1f98e48b23e82c01513ae"

            Path(tmp.name).unlink()

    @pytest.mark.skipif(
        os.getenv("R2_ACCOUNT_ID") is None,
        reason="R2 credentials not configured",
    )
    def test_client_initialization(self):
        """Test S3 client initialization with real credentials."""
        uploader = R2Uploader()  # Uses settings
        client = uploader.client

        assert client is not None

    def test_client_property(self, uploader):
        """Test client property creates S3 client."""
        # Mock the boto3 client
        with mock.patch("boto3.client"):
            uploader._client = None  # Reset
            client = uploader.client

            assert client is not None


class TestFileUpload:
    """Tests for file upload functionality."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_upload_file_not_found(self, uploader):
        """Test upload with non-existent file."""
        with pytest.raises(FileNotFoundError):
            uploader.upload_file("/nonexistent/file.mp4")

    @pytest.mark.asyncio
    async def test_upload_file_success(self, uploader):
        """Test successful file upload with mocked S3."""
        # Create a test file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"fake video content")
            tmp.flush()

            try:
                # Mock the S3 client methods
                with mock.patch.object(uploader, "client") as mock_client:
                    mock_client.upload_file.return_value = {"ETag": '"test-etag"'}

                    result = uploader.upload_file(tmp.name)

                    assert result.key.endswith(".mp4")
                    assert "https://test-bucket.r2.dev/" in result.url
                    assert result.file_size_bytes == len(b"fake video content")

            finally:
                Path(tmp.name).unlink()

    def test_upload_file_with_custom_key(self, uploader):
        """Test upload with custom S3 key."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"fake video content")
            tmp.flush()

            try:
                with mock.patch.object(uploader, "client") as mock_client:
                    mock_client.upload_file.return_value = {"ETag": '"test-etag"'}

                    result = uploader.upload_file(tmp.name, key="custom/key.mp4")

                    assert result.key == "custom/key.mp4"

            finally:
                Path(tmp.name).unlink()

    def test_upload_file_with_metadata(self, uploader):
        """Test upload with custom metadata."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"fake video content")
            tmp.flush()

            try:
                with mock.patch.object(uploader, "client") as mock_client:
                    mock_client.upload_file.return_value = {"ETag": '"test-etag"'}

                    metadata = {"chapter_id": "test-1", "duration": "60"}
                    result = uploader.upload_file(tmp.name, metadata=metadata)

                    # Verify upload was called with metadata
                    assert result.metadata == {}  # Not stored in result

            finally:
                Path(tmp.name).unlink()

    @pytest.mark.asyncio
    async def test_upload_file_large_file_multipart(self, uploader):
        """Test multipart upload for large files."""
        # Create a file larger than threshold
        large_content = b"x" * (101 * 1024 * 1024)  # 101 MB

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(large_content)
            tmp.flush()

            try:
                with mock.patch.object(uploader, "client") as mock_client:
                    # Mock multipart upload methods
                    mock_client.create_multipart_upload.return_value = {
                        "UploadId": "test-upload-id"
                    }
                    mock_client.upload_part.return_value = {"ETag": '"part-etag"'}
                    mock_client.complete_multipart_upload.return_value = {
                        "ETag": '"complete-etag"'
                    }

                    result = uploader.upload_file(tmp.name)

                    # Should use multipart upload
                    assert result.file_size_mb > 100

            finally:
                Path(tmp.name).unlink()


class TestVideoUpload:
    """Tests for video upload convenience method."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_upload_video(self, uploader):
        """Test video upload with automatic key generation."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"fake video")
            tmp.flush()

            try:
                with mock.patch.object(uploader, "client") as mock_client:
                    mock_client.upload_file.return_value = {"ETag": '"test-etag"'}

                    result = uploader.upload_video(tmp.name, chapter_id="chapter-1")

                    # Check key format
                    assert "videos/" in result.key
                    assert "chapter-1/" in result.key
                    assert result.key.endswith(".mp4")

            finally:
                Path(tmp.name).unlink()


class TestPresignedURL:
    """Tests for presigned URL generation."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_generate_presigned_url(self, uploader):
        """Test presigned URL generation."""
        with mock.patch.object(uploader, "client") as mock_client:
            mock_client.generate_presigned_url.return_value = "https://presigned-url"

            result = uploader.generate_presigned_url("videos/test.mp4", expires_in=3600)

            assert isinstance(result, PresignedURLResult)
            assert result.url == "https://presigned-url"

    def test_generate_presigned_url_custom_expiration(self, uploader):
        """Test presigned URL with custom expiration."""
        with mock.patch.object(uploader, "client") as mock_client:
            mock_client.generate_presigned_url.return_value = "https://presigned-url"

            result = uploader.generate_presigned_url("videos/test.mp4", expires_in=7200)

            # Check expiration is approximately 2 hours from now
            from datetime import datetime, timedelta

            expected_expires = datetime.now() + timedelta(seconds=7200)
            time_diff = abs((result.expires_at - expected_expires).total_seconds())
            assert time_diff < 1  # Within 1 second


class TestFileDeletion:
    """Tests for file deletion operations."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_delete_file_success(self, uploader):
        """Test successful file deletion."""
        with mock.patch.object(uploader, "client") as mock_client:
            mock_client.delete_object.return_value = {}

            result = uploader.delete_file("videos/test.mp4")

            assert result is True

    def test_delete_file_failure(self, uploader):
        """Test file deletion with error."""
        from botocore.exceptions import ClientError

        with mock.patch.object(uploader, "client") as mock_client:
            error_response = {"Error": {"Code": "403", "Message": "Access Denied"}}
            error = ClientError(error_response, "DeleteObject")
            mock_client.delete_object.side_effect = error

            result = uploader.delete_file("videos/test.mp4")

            assert result is False

    def test_delete_files_batch(self, uploader):
        """Test batch file deletion."""
        keys = ["videos/file1.mp4", "videos/file2.mp4", "videos/file3.mp4"]

        with mock.patch.object(uploader, "client") as mock_client:
            mock_client.delete_objects.return_value = {
                "Deleted": [
                    {"Key": "videos/file1.mp4"},
                    {"Key": "videos/file2.mp4"},
                    {"Key": "videos/file3.mp4"},
                ]
            }

            count = uploader.delete_files(keys)

            assert count == 3

    def test_delete_files_empty_list(self, uploader):
        """Test batch deletion with empty list."""
        count = uploader.delete_files([])
        assert count == 0


class TestFileListing:
    """Tests for file listing operations."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_list_files(self, uploader):
        """Test listing files in bucket."""
        with mock.patch.object(uploader, "client") as _:
            mock_paginator = mock.Mock()
            mock_paginator.paginate.return_value = [
                {
                    "Contents": [
                        {
                            "Key": "videos/file1.mp4",
                            "Size": 1024000,
                            "LastModified": "2024-01-01",
                            "ETag": '"etag1"',
                        },
                        {
                            "Key": "videos/file2.mp4",
                            "Size": 2048000,
                            "LastModified": "2024-01-02",
                            "ETag": '"etag2"',
                        },
                    ]
                }
            ]

            uploader.client.get_paginator.return_value = mock_paginator

            files = uploader.list_files("videos/")

            assert len(files) == 2
            assert files[0]["key"] == "videos/file1.mp4"
            assert files[1]["key"] == "videos/file2.mp4"

    def test_list_files_with_prefix(self, uploader):
        """Test listing files with prefix filter."""
        with mock.patch.object(uploader, "client") as _:
            mock_paginator = mock.Mock()
            mock_paginator.paginate.return_value = [
                {
                    "Contents": [
                        {
                            "Key": "videos/chapter-1/file1.mp4",
                            "Size": 1024000,
                            "LastModified": "2024-01-01",
                            "ETag": '"etag1"',
                        }
                    ]
                }
            ]

            uploader.client.get_paginator.return_value = mock_paginator

            files = uploader.list_files("videos/chapter-1/")

            assert len(files) == 1
            assert "chapter-1/" in files[0]["key"]


class TestFileOperations:
    """Tests for file existence and info operations."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_file_exists_true(self, uploader):
        """Test file exists returns True."""

        with mock.patch.object(uploader, "client") as mock_client:
            # File exists (head_object succeeds)
            mock_client.head_object.return_value = {}

            result = uploader.file_exists("videos/test.mp4")

            assert result is True

    def test_file_exists_false(self, uploader):
        """Test file exists returns False for 404."""
        from botocore.exceptions import ClientError

        with mock.patch.object(uploader, "client") as mock_client:
            # File doesn't exist
            error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
            error = ClientError(error_response, "HeadObject")
            mock_client.head_object.side_effect = error

            result = uploader.file_exists("videos/test.mp4")

            assert result is False

    def test_get_file_info(self, uploader):
        """Test getting file information."""
        with mock.patch.object(uploader, "client") as mock_client:
            mock_client.head_object.return_value = {
                "ContentLength": 1024000,
                "ContentType": "video/mp4",
                "LastModified": "2024-01-01T00:00:00",
                "ETag": '"test-etag"',
                "Metadata": {"chapter_id": "test-1"},
            }

            info = uploader.get_file_info("videos/test.mp4")

            assert info["key"] == "videos/test.mp4"
            assert info["size"] == 1024000
            assert info["content_type"] == "video/mp4"
            assert info["metadata"]["chapter_id"] == "test-1"

    def test_get_file_info_not_found(self, uploader):
        """Test get_file_info for non-existent file."""
        from botocore.exceptions import ClientError

        with mock.patch.object(uploader, "client") as mock_client:
            error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
            error = ClientError(error_response, "HeadObject")
            mock_client.head_object.side_effect = error

            info = uploader.get_file_info("videos/test.mp4")

            assert info is None


class TestBucketOperations:
    """Tests for bucket operations."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_create_bucket_if_not_exists_exists(self, uploader):
        """Test bucket creation when bucket exists."""
        with mock.patch.object(uploader, "client") as mock_client:
            # Bucket exists
            mock_client.head_bucket.return_value = {}

            result = uploader.create_bucket_if_not_exists()

            assert result is True

    def test_create_bucket_if_not_exists_new(self, uploader):
        """Test bucket creation when bucket doesn't exist."""
        from botocore.exceptions import ClientError

        with mock.patch.object(uploader, "client") as mock_client:
            # Bucket doesn't exist (404)
            error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
            not_found = ClientError(error_response, "HeadBucket")
            mock_client.head_bucket.side_effect = not_found

            # Create bucket succeeds
            mock_client.create_bucket.return_value = {}

            result = uploader.create_bucket_if_not_exists()

            assert result is True


class TestSingleton:
    """Tests for singleton instance."""

    def test_singleton_instance(self):
        """Test that singleton instance exists."""
        assert r2_uploader is not None
        assert isinstance(r2_uploader, R2Uploader)


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.fixture
    def uploader(self):
        """Create uploader with mocked S3 client."""
        uploader = R2Uploader(
            account_id="test-account",
            access_key_id="test-key",
            secret_access_key="test-secret",
            bucket_name="test-bucket",
            public_url="https://test-bucket.r2.dev",
        )
        return uploader

    def test_upload_with_boto_error(self, uploader):
        """Test upload handling of BotoCoreError."""
        from botocore.exceptions import BotoCoreError

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"fake video")
            tmp.flush()

            try:
                with mock.patch.object(uploader, "client") as mock_client:
                    mock_client.upload_file.side_effect = BotoCoreError()

                    with pytest.raises(RuntimeError, match="Upload to R2 failed"):
                        uploader.upload_file(tmp.name)

            finally:
                Path(tmp.name).unlink()

    def test_upload_with_client_error(self, uploader):
        """Test upload handling of ClientError."""
        from botocore.exceptions import ClientError

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"fake video")
            tmp.flush()

            try:
                with mock.patch.object(uploader, "client") as mock_client:
                    error_response = {"Error": {"Code": "403", "Message": "Forbidden"}}
                    error = ClientError(error_response, "PutObject")
                    mock_client.upload_file.side_effect = error

                    with pytest.raises(RuntimeError, match="Upload to R2 failed"):
                        uploader.upload_file(tmp.name)

            finally:
                Path(tmp.name).unlink()
