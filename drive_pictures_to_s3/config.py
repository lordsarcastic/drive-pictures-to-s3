from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional, cast
from google.auth import exceptions
from google.oauth2 import credentials, service_account


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Drive settings
    GOOGLE_DRIVE_FOLDER_ID: str = Field(..., description="ID of the Google Drive folder to process")

    # AWS settings
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., description="AWS secret access key")
    AWS_REGION: str = Field(..., description="AWS region")
    S3_BUCKET_NAME: str = Field(..., description="S3 bucket name")
    S3_PREFIX: Optional[str] = Field(default="", description="Prefix for S3 object keys")
    
    # Application settings
    RETAIN_FILENAMES: bool = Field(default=True, description="Whether to retain original filenames or use sequential numbers")
    # Google Cloud credentials (either JSON string or file path)
    GOOGLE_APPLICATION_CREDENTIALS_JSON: str | None = None
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None

    def get_google_credentials(self) -> credentials.Credentials:
        if self.GOOGLE_APPLICATION_CREDENTIALS_JSON:
            return cast(
                credentials.Credentials,
                service_account.Credentials.from_service_account_info(
                    self.GOOGLE_APPLICATION_CREDENTIALS_JSON,
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                ),
            )
        elif self.GOOGLE_APPLICATION_CREDENTIALS:
            try:
                return cast(
                    credentials.Credentials,
                    service_account.Credentials.from_service_account_file(
                        self.GOOGLE_APPLICATION_CREDENTIALS,
                        scopes=['https://www.googleapis.com/auth/drive.readonly']
                    ),
                )
            except exceptions.MalformedError:
                pass

            return cast(
                credentials.Credentials,
                credentials.Credentials.from_authorized_user_file(
                    self.GOOGLE_APPLICATION_CREDENTIALS,
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                ),
            )

        else:
            raise ValueError(
                "Either GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS_JSON "
                "must be set in the environment"
            )


settings = Settings()   # type: ignore