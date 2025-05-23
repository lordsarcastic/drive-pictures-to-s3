# Drive Pictures to S3

A Python application that transfers images from a Google Drive folder to AWS S3, with options to retain original filenames or use sequential numbering.

## Features

- Transfer images from Google Drive to AWS S3
- Configurable file naming (original names or sequential numbers)
- Comprehensive error handling and detailed logging using `loguru`
- Environment-based configuration
- Modular and maintainable code structure
- Docker support for easy deployment and execution

## Prerequisites

- Python 3.8 or higher (for local development)
- Docker (for running with Docker)
- Google Cloud project with Drive API enabled
- Google service account with access to the target Drive folder
- AWS account with S3 access
- AWS credentials with appropriate permissions

## Setup

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd drive-pictures-to-s3
    ```

2.  **Local Development Setup:**
    *   Create and activate a virtual environment:
        ```bash
        python -m venv .venv
        source .venv/bin/activate  # On Windows: .venv\Scripts\activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Set up Google Cloud:**
    *   Create a project in Google Cloud Console.
    *   Enable the Google Drive API.
    *   Create a service account.
    *   Download the service account key JSON file.
    *   Share the target Drive folder with the service account email address found in the JSON key file.

4.  **Configure environment variables:**
    *   Create a `.env` file in the root of the project (you can copy `example.env` or `.env.example` if one exists and rename it to `.env`).
    *   Fill in the required values in the `.env` file:
        *   `GOOGLE_DRIVE_FOLDER_ID`: ID of the Google Drive folder to process.
        *   `GOOGLE_APPLICATION_CREDENTIALS_JSON`: The JSON content of your service account key. (Alternatively, you can use `GOOGLE_APPLICATION_CREDENTIALS` to specify a file path, but `GOOGLE_APPLICATION_CREDENTIALS_JSON` is often easier for Docker).
        *   `AWS_ACCESS_KEY_ID`: AWS access key ID.
        *   `AWS_SECRET_ACCESS_KEY`: AWS secret access key.
        *   `AWS_REGION`: AWS region.
        *   `S3_BUCKET_NAME`: S3 bucket name.
        *   `S3_PREFIX` (Optional): Prefix for S3 object keys (e.g., `images/` or `my-photos/`). Defaults to no prefix.
        *   `RETAIN_FILENAMES`: Set to `True` to retain original filenames or `False` to use sequential numbers (e.g., `0001.jpg`, `0002.png`). Defaults to `True`.

## Usage

### Option 1: Running with Docker (Recommended)

1.  **Build the Docker image:**
    ```bash
    docker build -t drive-to-s3-importer .
    ```

2.  **Run the Docker container:**
    Make sure you have a `.env` file configured as described in the "Setup" section.
    ```bash
    docker run --rm --env-file .env drive-to-s3-importer
    ```
    *   `--rm`: Automatically removes the container when it exits.
    *   `--env-file .env`: Loads environment variables from the `.env` file.

### Option 2: Running Locally (Python)

1.  Ensure you have completed the "Local Development Setup" and "Configure environment variables" steps.

2.  Run the application:
    ```bash
    python drive_pictures_to_s3/main.py
    ```

The script will:
1.  Connect to Google Drive using the service account.
2.  List all images in the specified Drive folder.
3.  Download each image.
4.  Upload it to the configured S3 bucket, applying the chosen naming convention (original or sequential).
5.  Log progress and any errors to the console using `loguru`.

## Configuration Details

Environment variables are loaded from a `.env` file at the root of the project using `pydantic-settings`.

Key configuration options:

*   **`GOOGLE_DRIVE_FOLDER_ID`**: The unique identifier of the Google Drive folder from which to fetch images.
*   **`GOOGLE_APPLICATION_CREDENTIALS_JSON` or `GOOGLE_APPLICATION_CREDENTIALS`**: Provide either the JSON content directly or the path to the credentials file.
*   **`S3_BUCKET_NAME`**: The name of your AWS S3 bucket where images will be stored.
*   **`RETAIN_FILENAMES`**: Controls how files are named in S3. `True` keeps original names, `False` uses a sequential numeric prefix (e.g., `0001.ext`, `0002.ext`).
*   **`S3_PREFIX`**: If you want to store images in a specific "folder" within your S3 bucket, set this prefix (e.g., `backup/images/`).

## Error Handling

The application includes robust error handling:
- Individual file processing errors (e.g., a single file failing to download or upload) are logged, and the process continues with the next file.
- Critical errors (e.g., invalid AWS credentials, incorrect Drive Folder ID, inability to connect to Google Drive) will terminate the application with an error message.
- All logs provide context to help diagnose issues.

## Logging

Detailed logs are output to `stderr` (standard error) using the `loguru` library.
The default log format is: `{time} {level} {message}`.
This includes timestamps, log levels (INFO, ERROR, SUCCESS, DEBUG), and informative messages for each step of the process.

## Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/YourFeature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/YourFeature`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details (if one exists). 