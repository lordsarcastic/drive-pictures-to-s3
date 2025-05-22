from googleapiclient.discovery import build  # type: ignore
from googleapiclient.http import MediaIoBaseDownload  # type: ignore
import io
from typing import List, Dict, Any
from loguru import logger

from drive_pictures_to_s3.config import settings   # type: ignore


class DriveClient:
    """Client for interacting with Google Drive API."""
    
    def __init__(self) -> None:
        """Initialize the Google Drive client with credentials."""
        logger.info("Initializing DriveClient...")
        credentials = settings.get_google_credentials()
        self.service = build('drive', 'v3', credentials=credentials)
        logger.info("DriveClient initialized.")
    
    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all image files in the specified folder.
        
        Returns:
            List of dictionaries containing file metadata
        """
        logger.info(f"Listing files from Google Drive folder ID: {settings.GOOGLE_DRIVE_FOLDER_ID}")
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
            return files  # type: ignore
            
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
        logger.info(f"Downloading file with ID: {file_id} from Google Drive...")
        try:
            file_metadata = self.service.files().get(fileId=file_id, fields="name").execute()
            file_name = file_metadata.get('name')
            logger.info(f"Retrieved metadata for file ID: {file_id}, Filename: {file_name}")
            
            request = self.service.files().get_media(fileId=file_id)
            file_handle = io.BytesIO()
            downloader = MediaIoBaseDownload(file_handle, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"Download progress for {file_name}: {int(status.progress() * 100)}%")
            
            file_handle.seek(0)
            file_content = file_handle.getvalue()
            logger.success(f"Successfully downloaded {file_name} (ID: {file_id}), size: {len(file_content)} bytes")
            return file_content, file_name
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise 