from pydantic import BaseSettings, Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Drive settings
    GOOGLE_DRIVE_FOLDER_ID: str = Field(..., description="ID of the Google Drive folder to process")
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(..., description="Path to Google service account credentials file")
    
    # AWS settings
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., description="AWS secret access key")
    AWS_REGION: str = Field(..., description="AWS region")
    S3_BUCKET_NAME: str = Field(..., description="S3 bucket name")
    S3_PREFIX: Optional[str] = Field(default="", description="Prefix for S3 object keys")
    
    # Application settings
    RETAIN_FILENAMES: bool = Field(default=True, description="Whether to retain original filenames or use sequential numbers")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 