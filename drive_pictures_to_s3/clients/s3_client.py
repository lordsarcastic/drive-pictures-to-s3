import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional

from .config import settings

logger = logging.getLogger(__name__)


class S3Client:
    """Client for interacting with AWS S3."""
    
    def __init__(self):
        """Initialize the S3 client with credentials."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.S3_BUCKET_NAME
    
    def upload_file(self, file_content: bytes, file_name: str, counter: Optional[int] = None) -> str:
        """
        Upload a file to S3.
        
        Args:
            file_content: The file content as bytes
            file_name: Original file name
            counter: Optional counter for sequential naming
            
        Returns:
            The S3 object key
        """
        try:
            # Determine the S3 object key
            if settings.RETAIN_FILENAMES:
                object_key = f"{settings.S3_PREFIX}{file_name}"
            else:
                # Use counter for sequential naming
                if counter is None:
                    raise ValueError("Counter must be provided when RETAIN_FILENAMES is False")
                extension = file_name.split('.')[-1]
                object_key = f"{settings.S3_PREFIX}{counter:04d}.{extension}"
            
            # Upload the file
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=file_content
            )
            
            logger.info(f"Successfully uploaded {object_key} to S3")
            return object_key
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise 