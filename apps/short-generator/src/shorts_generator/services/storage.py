"""Cloudflare R2 storage service for video CDN.

This service handles:
- Uploading videos to R2 bucket
- Uploading thumbnails to R2 bucket
- Uploading captions to R2 bucket
- Generating signed URLs for access
- Auto-purging old content after 90 days

Cost: $0.015/GB storage + free egress
"""

import hashlib
import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Any

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from shorts_generator.core.config import settings

logger = logging.getLogger(__name__)

# R2 bucket configuration
BUCKET_NAME = settings.r2_bucket_name
ACCOUNT_ID = settings.r2_account_id
ACCESS_KEY_ID = settings.r2_access_key_id
SECRET_ACCESS_KEY = settings.r2_secret_access_key

# R2 endpoint URL
R2_ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"

# Signed URL expiration (7 days)
PRESIGNED_URL_EXPIRY = 3600 * 24 * 7

# Storage paths
VIDEO_PATH = "videos"
THUMBNAIL_PATH = "thumbnails"
CAPTIONS_PATH = "captions"


class R2StorageService:
    """Cloudflare R2 storage service for CDN delivery."""

    def __init__(self):
        """Initialize the R2 storage service."""
        self._client = None
        self._bucket = BUCKET_NAME

    def _get_client(self):
        """Get or create boto3 S3 client for R2."""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=R2_ENDPOINT,
                aws_access_key_id=ACCESS_KEY_ID,
                aws_secret_access_key=SECRET_ACCESS_KEY,
                config=BotoConfig(
                    signature_version="s3v4",
                    region_name="auto",
                ),
            )
        return self._client

    def _generate_key(self, path_prefix: str, file_id: str, extension: str) -> str:
        """Generate a storage key for a file.

        Args:
            path_prefix: Path prefix (videos, thumbnails, captions)
            file_id: Unique file identifier
            extension: File extension (e.g., ".mp4")

        Returns:
            Storage key path
        """
        return f"{path_prefix}/{file_id}{extension}"

    def _calculate_etag(self, file_path: str) -> str:
        """Calculate ETag (MD5 hash) for a file.

        Args:
            file_path: Path to file

        Returns:
            MD5 hash as hex string
        """
        hash_md5 = hashlib.md5()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    async def upload_video(
        self,
        file_path: str,
        video_id: str,
        content_type: str = "video/mp4",
    ) -> dict[str, Any]:
        """Upload a video file to R2 storage.

        Args:
            file_path: Local path to video file
            video_id: Unique video identifier
            content_type: MIME type of the video

        Returns:
            dict with storage_key, cdn_url, and metadata

        Raises:
            Exception: If upload fails
        """
        logger.info(f"Uploading video {video_id} to R2")

        try:
            client = self._get_client()

            # Generate storage key
            storage_key = self._generate_key(VIDEO_PATH, video_id, ".mp4")

            # Get file size
            file_size = os.path.getsize(file_path)

            # Upload file
            with open(file_path, "rb") as f:
                client.upload_fileobj(
                    f,
                    self._bucket,
                    storage_key,
                    ExtraArgs={
                        "ContentType": content_type,
                        "Metadata": {
                            "file-size": str(file_size),
                            "video-id": video_id,
                        },
                    },
                )

            # Generate CDN URL - use presigned URL if no custom domain
            if settings.r2_custom_domain:
                cdn_url = self.get_public_url(storage_key)
            else:
                # Use presigned URL (7 days expiration) when no custom domain is set
                cdn_url = self.generate_presigned_url(storage_key, expiration=PRESIGNED_URL_EXPIRY)
                logger.info(f"Using presigned URL (no custom domain configured)")

            logger.info(f"Video uploaded successfully: {storage_key} ({file_size} bytes)")

            return {
                "storage_key": storage_key,
                "cdn_url": cdn_url,
                "file_size": file_size,
                "bucket": self._bucket,
            }

        except ClientError as e:
            logger.error(f"R2 upload failed for video {video_id}: {e}")
            raise Exception(f"Video upload failed: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error uploading video {video_id}: {e}")
            raise

    async def upload_thumbnail(
        self,
        file_path: str,
        video_id: str,
        content_type: str = "image/jpeg",
    ) -> dict[str, Any]:
        """Upload a thumbnail image to R2 storage.

        Args:
            file_path: Local path to thumbnail file
            video_id: Associated video identifier
            content_type: MIME type of the image

        Returns:
            dict with storage_key, cdn_url, and metadata

        Raises:
            Exception: If upload fails
        """
        logger.info(f"Uploading thumbnail for video {video_id} to R2")

        try:
            client = self._get_client()

            # Generate storage key
            storage_key = self._generate_key(THUMBNAIL_PATH, video_id, ".jpg")

            # Get file size
            file_size = os.path.getsize(file_path)

            # Upload file
            with open(file_path, "rb") as f:
                client.upload_fileobj(
                    f,
                    self._bucket,
                    storage_key,
                    ExtraArgs={
                        "ContentType": content_type,
                        "CacheControl": "public, max-age=31536000",  # 1 year cache
                        "Metadata": {
                            "video-id": video_id,
                        },
                    },
                )

            # Generate CDN URL - use presigned URL if no custom domain
            if settings.r2_custom_domain:
                cdn_url = self.get_public_url(storage_key)
            else:
                # Use presigned URL (7 days expiration) when no custom domain is set
                cdn_url = self.generate_presigned_url(storage_key, expiration=PRESIGNED_URL_EXPIRY)
                logger.info(f"Using presigned URL for thumbnail (no custom domain configured)")

            logger.info(f"Thumbnail uploaded successfully: {storage_key}")

            return {
                "storage_key": storage_key,
                "cdn_url": cdn_url,
                "file_size": file_size,
                "bucket": self._bucket,
            }

        except ClientError as e:
            logger.error(f"R2 upload failed for thumbnail {video_id}: {e}")
            raise Exception(f"Thumbnail upload failed: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error uploading thumbnail {video_id}: {e}")
            raise

    async def upload_captions(
        self,
        captions_content: str,
        video_id: str,
        content_type: str = "text/plain",
    ) -> dict[str, Any]:
        """Upload caption content to R2 storage.

        Args:
            captions_content: SRT format captions
            video_id: Associated video identifier
            content_type: MIME type

        Returns:
            dict with storage_key, cdn_url, and metadata

        Raises:
            Exception: If upload fails
        """
        logger.info(f"Uploading captions for video {video_id} to R2")

        try:
            client = self._get_client()

            # Generate storage key
            storage_key = self._generate_key(CAPTIONS_PATH, video_id, ".srt")

            # Upload content
            client.put_object(
                Bucket=self._bucket,
                Key=storage_key,
                Body=captions_content.encode("utf-8"),
                ContentType=content_type,
                CacheControl="public, max-age=86400",  # 1 day cache
                Metadata={
                    "video-id": video_id,
                },
            )

            # Generate CDN URL - use presigned URL if no custom domain
            if settings.r2_custom_domain:
                cdn_url = self.get_public_url(storage_key)
            else:
                # Use presigned URL (7 days expiration) when no custom domain is set
                cdn_url = self.generate_presigned_url(storage_key, expiration=PRESIGNED_URL_EXPIRY)
                logger.info(f"Using presigned URL for captions (no custom domain configured)")

            logger.info(f"Captions uploaded successfully: {storage_key}")

            return {
                "storage_key": storage_key,
                "cdn_url": cdn_url,
                "content_length": len(captions_content),
                "bucket": self._bucket,
            }

        except ClientError as e:
            logger.error(f"R2 upload failed for captions {video_id}: {e}")
            raise Exception(f"Captions upload failed: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error uploading captions {video_id}: {e}")
            raise

    def get_public_url(self, storage_key: str) -> str:
        """Get the public CDN URL for a stored file.

        Args:
            storage_key: Storage key of the file

        Returns:
            Public CDN URL

        Note:
            This requires R2 bucket to have a custom domain configured.
            Falls back to direct R2 URL if custom domain not set.
        """
        # Use custom domain if configured (preferred for CDN)
        if settings.r2_custom_domain:
            return f"https://{settings.r2_custom_domain}/{storage_key}"

        # Fallback to direct R2 URL (no CDN benefits)
        return f"{R2_ENDPOINT}/{self._bucket}/{storage_key}"

    def generate_presigned_url(
        self,
        storage_key: str,
        expiration: int = PRESIGNED_URL_EXPIRY,
    ) -> str:
        """Generate a presigned URL for temporary access.

        Args:
            storage_key: Storage key of the file
            expiration: URL expiration time in seconds (default: 7 days)

        Returns:
            Presigned URL
        """
        try:
            client = self._get_client()
            return client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self._bucket,
                    "Key": storage_key,
                },
                ExpiresIn=expiration,
            )

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {storage_key}: {e}")
            raise

    async def delete_file(self, storage_key: str) -> bool:
        """Delete a file from R2 storage.

        Args:
            storage_key: Storage key of the file to delete

        Returns:
            True if successful

        Raises:
            Exception: If deletion fails
        """
        logger.info(f"Deleting file from R2: {storage_key}")

        try:
            client = self._get_client()
            client.delete_object(Bucket=self._bucket, Key=storage_key)

            logger.info(f"File deleted successfully: {storage_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to delete file {storage_key}: {e}")
            raise

    async def delete_video_files(self, video_id: str) -> dict[str, bool]:
        """Delete all files associated with a video.

        Args:
            video_id: Video identifier

        Returns:
            dict with deletion status for each file type
        """
        results = {
            "video": False,
            "thumbnail": False,
            "captions": False,
        }

        # Delete video
        try:
            video_key = self._generate_key(VIDEO_PATH, video_id, ".mp4")
            await self.delete_file(video_key)
            results["video"] = True
        except Exception:
            pass  # File may not exist

        # Delete thumbnail
        try:
            thumb_key = self._generate_key(THUMBNAIL_PATH, video_id, ".jpg")
            await self.delete_file(thumb_key)
            results["thumbnail"] = True
        except Exception:
            pass  # File may not exist

        # Delete captions
        try:
            captions_key = self._generate_key(CAPTIONS_PATH, video_id, ".srt")
            await self.delete_file(captions_key)
            results["captions"] = True
        except Exception:
            pass  # File may not exist

        return results

    async def list_files(
        self,
        path_prefix: str | None = None,
        max_keys: int = 1000,
    ) -> list[dict[str, Any]]:
        """List files in the bucket.

        Args:
            path_prefix: Optional path prefix to filter
            max_keys: Maximum number of keys to return

        Returns:
            List of file metadata
        """
        try:
            client = self._get_client()

            kwargs = {
                "Bucket": self._bucket,
                "MaxKeys": max_keys,
            }

            if path_prefix:
                kwargs["Prefix"] = path_prefix

            response = client.list_objects_v2(**kwargs)

            files = []
            for obj in response.get("Contents", []):
                files.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"],
                    "etag": obj["ETag"].strip('"'),
                })

            return files

        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            raise

    async def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics for the bucket.

        Returns:
            dict with file counts and total size by type
        """
        stats = {
            "videos": {"count": 0, "total_bytes": 0},
            "thumbnails": {"count": 0, "total_bytes": 0},
            "captions": {"count": 0, "total_bytes": 0},
        }

        # Get all files
        all_files = await self.list_files()

        for file in all_files:
            key = file["key"]
            size = file["size"]

            if key.startswith(VIDEO_PATH + "/"):
                stats["videos"]["count"] += 1
                stats["videos"]["total_bytes"] += size
            elif key.startswith(THUMBNAIL_PATH + "/"):
                stats["thumbnails"]["count"] += 1
                stats["thumbnails"]["total_bytes"] += size
            elif key.startswith(CAPTIONS_PATH + "/"):
                stats["captions"]["count"] += 1
                stats["captions"]["total_bytes"] += size

        # Calculate total size in GB
        total_bytes = sum(s["total_bytes"] for s in stats.values())
        total_gb = total_bytes / (1024**3)

        # Calculate estimated monthly cost
        monthly_cost = total_gb * 0.015  # $0.015 per GB

        stats["total"] = {
            "count": sum(s["count"] for s in stats.values()),
            "total_bytes": total_bytes,
            "total_gb": round(total_gb, 2),
            "estimated_monthly_cost_usd": round(monthly_cost, 4),
        }

        return stats


# Singleton instance
storage_service = R2StorageService()
