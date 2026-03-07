"""Cloudflare R2 Storage Service.

This service handles file uploads to Cloudflare R2:
- Video file uploads
- Multipart uploads for large files
- Presigned URL generation
- File deletion
- Bucket operations
- Progress tracking for uploads
"""

import hashlib
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.service_resource import S3ServiceResource

from shorts_generator.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Result of a file upload.

    Attributes:
        key: S3 key (path in bucket)
        url: Public URL of the uploaded file
        file_size_bytes: File size in bytes
        file_size_mb: File size in megabytes
        upload_time: Upload completion time
        etag: ETag of the uploaded object
        version_id: Version ID (if versioning is enabled)
    """

    key: str
    url: str
    file_size_bytes: int
    file_size_mb: float
    upload_time: datetime
    etag: str | None = None
    version_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "key": self.key,
            "url": self.url,
            "file_size_bytes": self.file_size_bytes,
            "file_size_mb": self.file_size_mb,
            "upload_time": self.upload_time.isoformat(),
            "etag": self.etag,
            "version_id": self.version_id,
            "metadata": self.metadata,
        }


@dataclass
class PresignedURLResult:
    """Result of presigned URL generation.

    Attributes:
        url: Presigned URL
        expires_at: When the URL expires
    """

    url: str
    expires_at: datetime


class R2Uploader:
    """Uploads files to Cloudflare R2 storage using S3-compatible API.

    Features:
    - Single file uploads
    - Multipart uploads for large files
    - Presigned URL generation
    - File deletion
    - Bucket listing
    - Progress tracking
    - Automatic retries
    """

    # Default settings
    DEFAULT_PART_SIZE_MB = 100  # Multipart upload part size
    MAX_SINGLE_PART_SIZE_MB = 100  # Use multipart for larger files

    def __init__(
        self,
        account_id: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        bucket_name: str | None = None,
        public_url: str | None = None,
    ):
        """Initialize the R2 uploader.

        Args:
            account_id: Cloudflare R2 account ID
            access_key_id: R2 access key ID
            secret_access_key: R2 secret access key
            bucket_name: Bucket name
            public_url: Public URL base (e.g., https://bucket.r2.dev)
        """
        self.account_id = account_id or settings.r2_account_id
        self.access_key_id = access_key_id or settings.r2_access_key_id
        self.secret_access_key = secret_access_key or settings.r2_secret_access_key
        self.bucket_name = bucket_name or settings.r2_bucket_name
        self.public_url = public_url or settings.r2_public_url

        # Initialize S3 client
        self._client: S3Client | None = None
        self._resource: S3ServiceResource | None = None

    @property
    def client(self) -> S3Client:
        """Get or create S3 client."""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name="auto",
            )
            logger.info("R2 S3 client initialized")
        return self._client

    @property
    def resource(self) -> S3ServiceResource:
        """Get or create S3 resource."""
        if self._resource is None:
            self._resource = boto3.resource(
                "s3",
                endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name="auto",
            )
        return self._resource

    def _calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 hash of file.

        Args:
            file_path: Path to file

        Returns:
            MD5 hash as hex string
        """
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def _get_content_type(self, file_path: str) -> str:
        """Get content type based on file extension.

        Args:
            file_path: Path to file

        Returns:
            Content type string
        """
        ext = Path(file_path).suffix.lower()

        content_types = {
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".mkv": "video/x-matroska",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
            ".json": "application/json",
            ".txt": "text/plain",
            ".xml": "application/xml",
        }

        return content_types.get(ext, "application/octet-stream")

    def _generate_key(
        self,
        base_key: str,
        prefix: str = "videos",
        timestamp: bool = True,
    ) -> str:
        """Generate S3 key for upload.

        Args:
            base_key: Base key/filename
            prefix: Key prefix (folder)
            timestamp: Add timestamp to key

        Returns:
            Full S3 key
        """
        # Sanitize base key
        safe_key = base_key.replace("\\", "/").lstrip("/")

        # Add timestamp if requested
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d/%H%M%S")
            return f"{prefix}/{timestamp_str}/{safe_key}"

        return f"{prefix}/{safe_key}"

    def _get_public_url(self, key: str) -> str:
        """Get public URL for an S3 key.

        Args:
            key: S3 key

        Returns:
            Public URL
        """
        # Remove leading slash if present
        key = key.lstrip("/")
        return f"{self.public_url}/{key}"

    def upload_file(
        self,
        file_path: str,
        key: str | None = None,
        metadata: dict[str, str] | None = None,
        content_type: str | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> UploadResult:
        """Upload a file to R2.

        Args:
            file_path: Path to file to upload
            key: S3 key (default: auto-generated)
            metadata: Custom metadata to attach
            content_type: Content type (default: auto-detected)
            progress_callback: Optional callback for progress (uploaded_bytes, total_bytes)

        Returns:
            UploadResult with upload information

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If upload fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        # Generate key if not provided
        if key is None:
            filename = Path(file_path).name
            key = self._generate_key(filename)

        # Detect content type if not provided
        if content_type is None:
            content_type = self._get_content_type(file_path)

        logger.info(
            f"Uploading {file_path} to R2: {self.bucket_name}/{key} ({file_size_mb:.2f}MB)"
        )

        extra_args: dict[str, Any] = {"ContentType": content_type}

        if metadata:
            extra_args["Metadata"] = metadata

        try:
            # For large files, use multipart upload
            if file_size_mb > self.MAX_SINGLE_PART_SIZE_MB:
                return self._upload_multipart(
                    file_path=file_path,
                    key=key,
                    extra_args=extra_args,
                    progress_callback=progress_callback,
                )

            # Single part upload
            upload_args: dict[str, Any] = {
                "Bucket": self.bucket_name,
                "Key": key,
                "FilePath": file_path,
                "ExtraArgs": extra_args,
            }

            if progress_callback:
                upload_args["Callback"] = progress_callback

            result = self.client.upload_file(**upload_args)

            upload_result = UploadResult(
                key=key,
                url=self._get_public_url(key),
                file_size_bytes=file_size,
                file_size_mb=file_size_mb,
                upload_time=datetime.now(),
                etag=result.get("ETag", "").strip('"'),
            )

            logger.info(f"✅ Upload complete: {upload_result.url}")

            return upload_result

        except (BotoCoreError, ClientError) as e:
            logger.error(f"R2 upload failed: {e}")
            raise RuntimeError(f"Upload to R2 failed: {e}") from e

    def _upload_multipart(
        self,
        file_path: str,
        key: str,
        extra_args: dict[str, Any],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> UploadResult:
        """Upload large file using multipart upload.

        Args:
            file_path: Path to file
            key: S3 key
            extra_args: Extra arguments for upload
            progress_callback: Optional progress callback

        Returns:
            UploadResult
        """
        file_size = os.path.getsize(file_path)
        part_size = self.DEFAULT_PART_SIZE_MB * 1024 * 1024

        logger.info(f"Using multipart upload (file size: {file_size / (1024*1024):.2f}MB)")

        try:
            # Initiate multipart upload
            mpu = self.client.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                **extra_args,
            )

            upload_id = mpu["UploadId"]
            parts = []

            # Upload parts
            with open(file_path, "rb") as f:
                part_number = 1
                uploaded_bytes = 0

                while True:
                    part_data = f.read(part_size)
                    if not part_data:
                        break

                    part = self.client.upload_part(
                        Bucket=self.bucket_name,
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=part_data,
                    )

                    parts.append({"PartNumber": part_number, "ETag": part["ETag"]})

                    uploaded_bytes += len(part_data)

                    if progress_callback:
                        progress_callback(uploaded_bytes, file_size)

                    logger.info(f"Part {part_number} uploaded")
                    part_number += 1

            # Complete multipart upload
            result = self.client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )

            file_size_mb = file_size / (1024 * 1024)

            return UploadResult(
                key=key,
                url=self._get_public_url(key),
                file_size_bytes=file_size,
                file_size_mb=file_size_mb,
                upload_time=datetime.now(),
                etag=result.get("ETag", "").strip('"'),
            )

        except (BotoCoreError, ClientError):
            # Abort on failure
            try:
                self.client.abort_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=key,
                    UploadId=upload_id,
                )
            except Exception:
                pass
            raise

    def upload_video(
        self,
        video_path: str,
        chapter_id: str,
        metadata: dict[str, str] | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> UploadResult:
        """Upload a video file to R2.

        Convenience method for video uploads with automatic key generation.

        Args:
            video_path: Path to video file
            chapter_id: Chapter/lesson identifier
            metadata: Optional metadata (title, duration, etc.)
            progress_callback: Optional progress callback

        Returns:
            UploadResult
        """
        filename = Path(video_path).name
        key = self._generate_key(
            base_key=f"{chapter_id}/{filename}",
            prefix="videos",
        )

        # Add video metadata
        if metadata is None:
            metadata = {}

        metadata["chapter_id"] = chapter_id
        metadata["upload_type"] = "video"

        return self.upload_file(
            file_path=video_path,
            key=key,
            metadata=metadata,
            progress_callback=progress_callback,
        )

    def generate_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
        operation: Literal["get_object", "put_object"] = "get_object",
    ) -> PresignedURLResult:
        """Generate a presigned URL for private access.

        Args:
            key: S3 key
            expires_in: Expiration time in seconds (default: 1 hour)
            operation: Operation to generate URL for

        Returns:
            PresignedURLResult with URL and expiration
        """
        try:
            url = self.client.generate_presigned_url(
                ClientMethod=f"{operation}",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                },
                ExpiresIn=expires_in,
            )

            expires_at = datetime.now() + timedelta(seconds=expires_in)

            return PresignedURLResult(
                url=url,
                expires_at=expires_at,
            )

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Presigned URL generation failed: {e}")
            raise

    def delete_file(self, key: str) -> bool:
        """Delete a file from R2.

        Args:
            key: S3 key of file to delete

        Returns:
            True if successful
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            logger.info(f"Deleted: {key}")
            return True

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Delete failed for {key}: {e}")
            return False

    def delete_files(self, keys: list[str]) -> int:
        """Delete multiple files from R2.

        Args:
            keys: List of S3 keys to delete

        Returns:
            Number of files deleted
        """
        if not keys:
            return 0

        try:
            # Delete objects (batch delete supports up to 1000 keys)
            response = self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={"Objects": [{"Key": key} for key in keys]},
            )

            deleted_count = len(response.get("Deleted", []))
            logger.info(f"Deleted {deleted_count} files")

            return deleted_count

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Batch delete failed: {e}")
            return 0

    def list_files(
        self,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[dict[str, Any]]:
        """List files in the bucket.

        Args:
            prefix: Key prefix to filter
            max_keys: Maximum number of keys to return

        Returns:
            List of file info dictionaries
        """
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix,
                PaginationConfig={"MaxItems": max_keys, "PageSize": 100},
            )

            files = []
            for page in pages:
                for obj in page.get("Contents", []):
                    files.append({
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj.get("ETag", "").strip('"'),
                    })

            return files

        except (BotoCoreError, ClientError) as e:
            logger.error(f"List files failed: {e}")
            return []

    def file_exists(self, key: str) -> bool:
        """Check if a file exists in R2.

        Args:
            key: S3 key to check

        Returns:
            True if file exists
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def get_file_info(self, key: str) -> dict[str, Any] | None:
        """Get information about a file.

        Args:
            key: S3 key

        Returns:
            File info dict or None if not found
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            return {
                "key": key,
                "size": response.get("ContentLength", 0),
                "content_type": response.get("ContentType", ""),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag", "").strip('"'),
                "metadata": response.get("Metadata", {}),
            }

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return None
            raise

    def create_bucket_if_not_exists(self) -> bool:
        """Create the bucket if it doesn't exist.

        Returns:
            True if bucket exists or was created
        """
        try:
            # Check if bucket exists
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # Bucket doesn't exist, create it
                try:
                    region = self.client.meta.region_name
                    self.client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": region},
                    )
                    logger.info(f"Created bucket: {self.bucket_name}")
                    return True

                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    return False

            raise


# Singleton instance (lazy initialization)
r2_uploader: R2Uploader | None = None


def get_r2_uploader() -> R2Uploader:
    """Get or create the R2 uploader singleton (lazy initialization)."""
    global r2_uploader
    if r2_uploader is None:
        logger.info("Creating R2 uploader singleton")
        r2_uploader = R2Uploader()
        logger.info("R2 uploader singleton created")
    return r2_uploader
