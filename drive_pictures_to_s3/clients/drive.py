import asyncio
import io
import os
from typing import Any, Dict, List, cast

from config import settings  # type: ignore
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.http import MediaIoBaseDownload  # type: ignore
from loguru import logger

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Constants for rate limiting and retries
MAX_CONCURRENT_DOWNLOADS = 1  # Limit concurrent downloads
MAX_RETRIES = 3  # Maximum number of retry attempts
RETRY_DELAY = 2  # Delay between retries in seconds


class DriveClient:
    """Client for interacting with Google Drive API."""

    def __init__(self) -> None:
        """Initialize the Google Drive client with credentials."""
        logger.info("Initializing DriveClient...")
        credentials = self.get_credentials()
        self.service = build("drive", "v3", credentials=credentials)
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)  # Added
        logger.info("DriveClient initialized.")

    @classmethod
    def initialize_auth_flow(cls) -> Credentials:
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_OAUTH_CREDENTIALS, scopes=SCOPES
        )
        credentials = flow.run_local_server(port=0)
        return cast(Credentials, credentials)

    @classmethod
    def write_credentials_to_file(cls, credentials: str) -> None:
        with open(settings.GOOGLE_TOKEN_CREDENTIALS_LOCATION, "w") as f:
            f.write(credentials)

    @classmethod
    def get_credentials_from_file(cls) -> Credentials:
        credentials = Credentials.from_authorized_user_file(
            settings.GOOGLE_TOKEN_CREDENTIALS_LOCATION, scopes=SCOPES
        )
        return cast(Credentials, credentials)

    @classmethod
    def get_credentials(cls) -> Credentials:
        if not os.path.exists(settings.GOOGLE_TOKEN_CREDENTIALS_LOCATION):
            logger.info("No credentials found, initializing auth flow...")
            credentials = cls.initialize_auth_flow()
            cls.write_credentials_to_file(credentials.to_json())
            logger.success("Credentials written to file.")
            return credentials

        logger.info("Credentials found, loading from file...")
        credentials = cls.get_credentials_from_file()
        if credentials and credentials.expired and credentials.refresh_token:
            logger.info("Credentials expired, refreshing...")
            credentials.refresh(Request())
            logger.success("Credentials refreshed.")
        return credentials

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all image files in the specified folder.

        Returns:
            List of dictionaries containing file metadata
        """
        logger.info(
            "Listing files from Google Drive folder ID:"
            f"{settings.GOOGLE_DRIVE_FOLDER_ID}"
        )
        try:
            # Query for image files in the specified folder
            query = (
                f"'{settings.GOOGLE_DRIVE_FOLDER_ID}' "
                "in parents and mimeType contains 'image/'"
            )
            results = (
                self.service.files()
                .list(q=query, fields="files(id, name, mimeType)", pageSize=1000)
                .execute()
            )

            files = results.get("files", [])
            logger.info(f"Found {len(files)} image files in the folder")
            return files  # type: ignore

        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise

    async def download_file(self, file_id: str) -> tuple[bytes, str]:
        """
        Download a file from Google Drive with rate limiting and retries.

        Args:
            file_id: The ID of the file to download

        Returns:
            Tuple of (file content as bytes, file name)
        """
        logger.info(f"Downloading file with ID: {file_id} from Google Drive...")

        async with self.semaphore:  # Added: Rate limiting
            for attempt in range(MAX_RETRIES):  # Added: Retry logic
                try:
                    return await asyncio.to_thread(self._blocking_download, file_id)
                except Exception as e:
                    if attempt < MAX_RETRIES - 1:  # Don't sleep on the last attempt
                        logger.warning(
                            f"Attempt {attempt + 1}/{MAX_RETRIES} failed for file {file_id}. "  # noqa: E501
                            f"Error: {str(e)}. Retrying in {RETRY_DELAY} seconds..."
                        )
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        logger.error(f"Error downloading file {file_id}: {str(e)}")
                        raise
            # This return will never be reached, but it satisfies the linter
            raise RuntimeError("Unexpected end of retry loop")  # Added

    def _blocking_download(self, file_id: str) -> tuple[bytes, str]:
        """
        Blocking implementation of file download.
        This is called by download_file through asyncio.to_thread.
        """
        try:
            file_metadata = (
                self.service.files().get(fileId=file_id, fields="name").execute()
            )
            file_name = file_metadata.get("name")
            logger.info(
                f"Retrieved metadata for file ID: {file_id}, Filename: {file_name}"
            )

            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(
                        f"Download progress for {file_name}: "
                        f"{int(status.progress() * 100)}%"
                    )

            file_handle.seek(0)
            file_content = file_handle.getvalue()
            logger.success(
                f"Successfully downloaded {file_name} (ID: {file_id}), "
                f"size: {len(file_content)} bytes"
            )
            return file_content, file_name

        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise
