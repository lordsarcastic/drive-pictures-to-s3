import sys

from clients import DriveClient, S3Client
from config import settings
from loguru import logger

# Configure logging
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


class ImageTransfer:
    """Main class for handling image transfer from Google Drive to S3."""

    def __init__(self) -> None:
        """Initialize the image transfer process."""
        logger.info("Initializing ImageTransfer...")
        self.drive_client = DriveClient()
        self.s3_client = S3Client()
        logger.info("ImageTransfer initialized.")

    def process_files(self) -> None:
        """Process all files in the specified Google Drive folder."""
        logger.info("Starting file processing...")
        try:
            # List files from Google Drive
            files = self.drive_client.list_files()
            if not files:
                logger.info("No files found in the specified folder")
                return

            logger.info(f"Found {len(files)} files to process.")
            # Process each file
            for index, file in enumerate(files, start=1):
                file_id = file["id"]
                file_name_display = file.get("name", file_id)
                logger.info(
                    f"Processing file {index}/{len(files)}: "
                    f"{file_name_display} (ID: {file_id})"
                )
                try:
                    # Download file from Google Drive
                    file_content, file_name = self.drive_client.download_file(file_id)

                    # Upload to S3
                    counter = None if settings.RETAIN_FILENAMES else index
                    s3_key = self.s3_client.upload_file(
                        file_content, file_name, counter
                    )
                    logger.success(
                        f"Successfully processed and uploaded "
                        f"{file_name_display} to S3 as {s3_key}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error processing file {file.get('name', 'unknown')}: {str(e)}"
                    )
                    continue

            logger.info("File transfer process completed")

        except Exception as e:
            logger.error(f"Error in file transfer process: {str(e)}")
            sys.exit(1)
        finally:
            logger.info("File processing finished.")


def main() -> None:
    """Main entry point for the application."""
    logger.info("Application starting...")
    try:
        transfer = ImageTransfer()
        transfer.process_files()
        logger.info("Application finished successfully.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Application ended.")


if __name__ == "__main__":
    main()
