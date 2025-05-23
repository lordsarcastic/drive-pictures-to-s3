from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Drive settings
    GOOGLE_DRIVE_FOLDER_ID: str = Field(
        ..., description="ID of the Google Drive folder to process"
    )

    # AWS settings
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., description="AWS secret access key")
    AWS_REGION: str = Field(..., description="AWS region")
    S3_BUCKET_NAME: str = Field(..., description="S3 bucket name")
    S3_PREFIX: Optional[str] = Field(
        default="", description="Prefix for S3 object keys"
    )

    # Application settings
    RETAIN_FILENAMES: bool = Field(
        default=True,
        description="Whether to retain original filenames or use sequential numbers",
    )
    GOOGLE_OAUTH_CREDENTIALS: str = Field(..., description="Google OAuth credentials")
    GOOGLE_TOKEN_CREDENTIALS_LOCATION: str = Field(
        default="token.json", description="Location to save Google token credentials"
    )


settings = Settings()  # type: ignore
