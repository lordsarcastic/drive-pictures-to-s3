from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from typing import List, Dict, Any
import logging

from ..config import settings   # type: ignore

logger = logging.getLogger(__name__)


class DriveClient:
    """Client for interacting with Google Drive API."""
    
    def __init__(self) -> None:
        """Initialize the Google Drive client with credentials."""
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=credentials)
    
    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all image files in the specified folder.
        
        Returns:
            List of dictionaries containing file metadata
        """
        try:
            # Query for image files in the specified folder
            query = f"'{settings.GOOGLE_DRIVE_FOLDER_ID}' in parents and mimeType contains 'image/'"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)",
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} image files in the folder")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise
    
    def download_file(self, file_id: str) -> tuple[bytes, str]:
        """
        Download a file from Google Drive.
        
        Args:
            file_id: The ID of the file to download
            
        Returns:
            Tuple of (file content as bytes, file name)
        """
        try:
            file_metadata = self.service.files().get(fileId=file_id, fields="name").execute()
            file_name = file_metadata.get('name')
            
            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            file_handle.seek(0)
            return file_handle.getvalue(), file_name
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise 