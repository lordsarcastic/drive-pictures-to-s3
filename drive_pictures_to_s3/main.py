import logging
import sys

from config import settings
from clients import DriveClient, S3Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImageTransfer:
    """Main class for handling image transfer from Google Drive to S3."""
    
    def __init__(self) -> None:
        """Initialize the image transfer process."""
        self.drive_client = DriveClient()
        self.s3_client = S3Client()
    
    def process_files(self) -> None:
        """Process all files in the specified Google Drive folder."""
        try:
            # List files from Google Drive
            files = self.drive_client.list_files()
            if not files:
                logger.info("No files found in the specified folder")
                return
            
            # Process each file
            for index, file in enumerate(files, start=1):
                try:
                    # Download file from Google Drive
                    file_content, file_name = self.drive_client.download_file(file['id'])
                    
                    # Upload to S3
                    counter = None if settings.RETAIN_FILENAMES else index
                    self.s3_client.upload_file(file_content, file_name, counter)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file.get('name', 'unknown')}: {str(e)}")
                    continue
            
            logger.info("File transfer process completed")
            
        except Exception as e:
            logger.error(f"Error in file transfer process: {str(e)}")
            sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    try:
        transfer = ImageTransfer()
        transfer.process_files()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
