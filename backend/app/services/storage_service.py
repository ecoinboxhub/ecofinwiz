"""
Cloud file storage service for document uploads.

Supports AWS S3 (primary), Cloudinary (backup), or local disk (dev).
Replaces local disk storage in intelligence/service.py for production.
"""

import os
import uuid
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class StorageResult:
    success: bool
    url: Optional[str] = None
    path: Optional[str] = None
    error: Optional[str] = None


class S3StorageService:
    """AWS S3 cloud storage (primary for production)."""

    def __init__(self):
        self.bucket = settings.s3_bucket_name
        self.region = settings.s3_region or "eu-west-1"
        self.access_key = settings.s3_access_key_id
        self.secret_key = settings.s3_secret_access_key
        self.endpoint_url = settings.s3_endpoint_url
        self.use_path_style = settings.s3_use_path_style

    @property
    def is_configured(self) -> bool:
        return bool(self.access_key and self.secret_key and self.bucket)

    async def upload(self, file_bytes: bytes, filename: str, content_type: str) -> StorageResult:
        if not self.is_configured:
            return StorageResult(success=False, error="S3 not configured")

        try:
            import aioboto3
            from botocore.config import Config

            key = f"uploads/{uuid.uuid4()}-{filename}"
            config = Config(s3={"addressing_style": "path" if self.use_path_style else "virtual"})

            session = aioboto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )
            async with session.client("s3", endpoint_url=self.endpoint_url, config=config) as s3:
                await s3.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=file_bytes,
                    ContentType=content_type,
                )
                url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
                return StorageResult(success=True, url=url, path=key)

        except ImportError:
            logger.warning("S3: aioboto3 not installed, falling back to local storage")
            return StorageResult(success=False, error="aioboto3 not installed")
        except Exception as e:
            logger.error("S3 upload error: %s", e)
            return StorageResult(success=False, error=str(e))

    async def delete(self, key: str) -> bool:
        try:
            import aioboto3
            session = aioboto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )
            async with session.client("s3", endpoint_url=self.endpoint_url) as s3:
                await s3.delete_object(Bucket=self.bucket, Key=key)
                return True
        except Exception as e:
            logger.error("S3 delete error: %s", e)
            return False

    async def get_download_url(self, key: str, expires: int = 3600) -> Optional[str]:
        try:
            import aioboto3
            session = aioboto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )
            async with session.client("s3", endpoint_url=self.endpoint_url) as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": key},
                    ExpiresIn=expires,
                )
                return url
        except Exception as e:
            logger.error("S3 presigned URL error: %s", e)
            return None


class LocalStorageService:
    """Local disk storage (development fallback)."""

    def __init__(self):
        self.base_dir = settings.local_storage_dir or os.path.join(
            os.path.dirname(__file__), "..", "uploads"
        )
        os.makedirs(self.base_dir, exist_ok=True)

    async def upload(self, file_bytes: bytes, filename: str, content_type: str) -> StorageResult:
        key = f"{uuid.uuid4()}-{filename}"
        filepath = os.path.join(self.base_dir, key)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        return StorageResult(
            success=True,
            url=f"/uploads/{key}",
            path=filepath,
        )

    async def delete(self, key: str) -> bool:
        filepath = os.path.join(self.base_dir, key)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    async def get_download_url(self, key: str, expires: int = 3600) -> Optional[str]:
        return f"/uploads/{key}"


def get_storage_service():
    """Returns the appropriate storage service based on configuration."""
    s3 = S3StorageService()
    if s3.is_configured:
        logger.info("Storage: using AWS S3 (%s/%s)", s3.bucket, s3.region)
        return s3
    logger.info("Storage: using local disk (%s)", LocalStorageService().base_dir)
    return LocalStorageService()
