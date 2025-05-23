import asyncio
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

    async def _process_single_file(
        self, file_data: dict, index: int, total_files: int
    ) -> None:
        file_id = file_data["id"]
        file_name_display = file_data.get("name", file_id)
        logger.info(
            f"Processing file {index}/{total_files}: "
            f"{file_name_display} (ID: {file_id})"
        )
        try:
            # Download file from Google Drive
            file_content, file_name = await self.drive_client.download_file(file_id)

            # Upload to S3
            counter = None if settings.RETAIN_FILENAMES else index
            s3_key = await self.s3_client.upload_file(file_content, file_name, counter)
            logger.success(
                f"Successfully processed and uploaded "
                f"{file_name_display} to S3 as {s3_key}"
            )
        except Exception as e:
            logger.error(f"Error processing file {file_name_display}: {str(e)}")

    async def process_files(self) -> None:
        """Process all files in the specified Google Drive folder concurrently."""
        logger.info("Starting file processing...")
        try:
            # List files from Google Drive - this remains synchronous for now.
            # If listing becomes a bottleneck, it can also be made async.
            files = self.drive_client.list_files()
            if not files:
                logger.info("No files found in the specified folder")
                return

            logger.info(f"Found {len(files)} files to process.")

            tasks = []
            for index, file_data in enumerate(files, start=1):
                tasks.append(self._process_single_file(file_data, index, len(files)))

            await asyncio.gather(*tasks)

            logger.info("File transfer process completed")

        except Exception as e:
            logger.error(f"Error in file transfer process: {str(e)}")
            sys.exit(1)
        finally:
            logger.info("File processing finished.")


async def main() -> None:
    """Main entry point for the application."""
    logger.info("Application starting...")
    try:
        transfer = ImageTransfer()
        await transfer.process_files()
        logger.info("Application finished successfully.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Application ended.")


if __name__ == "__main__":
    asyncio.run(main())
