import asyncio
from typing import Optional

import boto3  # type: ignore
from botocore.exceptions import ClientError  # type: ignore
from config import settings  # type: ignore
from loguru import logger

# Constants for rate limiting
MAX_CONCURRENT_UPLOADS = 5  # Limit concurrent uploads


class S3Client:
    """Client for interacting with AWS S3."""

    def __init__(self) -> None:
        """Initialize the S3 client with credentials."""
        logger.info("Initializing S3Client...")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket = settings.S3_BUCKET_NAME
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_UPLOADS)  # Added
        logger.info(
            f"S3Client initialized. Bucket: {self.bucket}, "
            f"Region: {settings.AWS_REGION}"
        )

    async def upload_file(
        self, file_content: bytes, file_name: str, counter: Optional[int] = None
    ) -> str:
        """
        Upload a file to S3.

        Args:
            file_content: The file content as bytes
            file_name: Original file name
            counter: Optional counter for sequential naming

        Returns:
            The S3 object key
        """
        logger.info(
            f"Attempting to upload {file_name} to " f"S3 bucket {self.bucket}..."
        )

        async with self.semaphore:  # Added: Rate limiting
            try:
                # Determine the S3 object key
                if settings.RETAIN_FILENAMES:
                    object_key = f"{settings.S3_PREFIX}{file_name}"
                else:
                    # Use counter for sequential naming
                    if counter is None:
                        logger.error(
                            "Counter must be provided when "
                            "RETAIN_FILENAMES is False and is None."
                        )
                        raise ValueError(
                            "Counter must be provided when " "RETAIN_FILENAMES is False"
                        )
                    extension = file_name.split(".")[-1]
                    object_key = f"{settings.S3_PREFIX}{counter}.{extension}"

                # Upload the file
                await asyncio.to_thread(
                    self.s3_client.put_object,
                    Bucket=self.bucket,
                    Key=object_key,
                    Body=file_content,
                )

                logger.info(
                    f"Successfully uploaded {object_key} to "
                    f"S3 bucket {self.bucket}."
                )
                return object_key

            except ClientError as e:
                logger.error(f"Error uploading file to S3: {str(e)}")
                raise
            except ValueError as e:
                logger.error(f"ValueError during S3 upload logic: {str(e)}")
                raise
