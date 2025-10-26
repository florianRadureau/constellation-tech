"""
Cloud Storage service for image uploads.

Uploads generated constellation images to Google Cloud Storage.
"""

import io
import logging
import os
import uuid

import google.auth
from google.cloud import storage
from google.oauth2 import service_account
from PIL import Image

from config import settings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Exception for storage operations."""

    pass


class StorageService:
    """
    Upload images to Google Cloud Storage.

    Example:
        >>> storage = StorageService()
        >>> url = await storage.upload(image, "my-constellation.png")
        >>> print(url)  # Signed URL valid for 7 days
    """

    def __init__(self) -> None:
        """Initialize storage client with credentials."""
        self._initialize_client()
        logger.info(f"StorageService initialized (bucket: {settings.gcs_bucket_name})")

    def _initialize_client(self) -> None:
        """
        Initialize Google Cloud Storage client.

        Uses service account file in development or default credentials in production (Cloud Run).
        """
        credentials_path = settings.google_application_credentials

        # Check if credentials file exists (local development)
        if os.path.exists(credentials_path):
            logger.info(f"Using service account file: {credentials_path}")
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
        else:
            # Production (Cloud Run) - use default credentials
            logger.info("Using default environment credentials (Cloud Run)")
            credentials, _ = google.auth.default()

        self.client = storage.Client(
            project=settings.gcp_project_id, credentials=credentials
        )
        self.bucket = self.client.bucket(settings.gcs_bucket_name)

    async def upload(
        self, image: Image.Image, filename: str | None = None
    ) -> str:
        """
        Upload image to Cloud Storage and return public URL.

        Args:
            image: PIL Image to upload
            filename: Optional filename (generates UUID if not provided)

        Returns:
            Public URL to the uploaded image

        Raises:
            StorageError: If upload fails

        Example:
            >>> url = await storage.upload(image)
            >>> print(url)  # https://storage.googleapis.com/bucket/file.png
        """
        if filename is None:
            filename = f"{uuid.uuid4()}.png"

        # Ensure .png extension
        if not filename.endswith(".png"):
            filename += ".png"

        logger.info(f"Uploading image: {filename}")

        try:
            # Convert image to bytes
            image_bytes = self._image_to_bytes(image)

            # Create blob
            blob = self.bucket.blob(filename)

            # Upload with metadata
            blob.upload_from_string(
                image_bytes, content_type="image/png", timeout=60
            )

            # Make blob publicly accessible
            blob.make_public()

            logger.info(
                f"Upload successful ({len(image_bytes)} bytes) - {filename}"
            )

            # Return public URL
            url = blob.public_url

            return url

        except Exception as e:
            raise StorageError(f"Failed to upload image: {e}") from e

    def _image_to_bytes(self, image: Image.Image) -> bytes:
        """
        Convert PIL Image to PNG bytes.

        Args:
            image: PIL Image

        Returns:
            PNG bytes
        """
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return buffer.read()

    def delete(self, filename: str) -> bool:
        """
        Delete image from storage.

        Args:
            filename: Filename to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            blob = self.bucket.blob(filename)
            blob.delete()
            logger.info(f"Deleted: {filename}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete {filename}: {e}")
            return False
