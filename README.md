# Drive Pictures to S3

A Python application that transfers images from a Google Drive folder to AWS S3, with options to retain original filenames or use sequential numbering.

## Features

- Transfer images from Google Drive to AWS S3
- Configurable file naming (original names or sequential numbers)
- Comprehensive error handling and detailed logging using `loguru`
- Environment-based configuration
- Modular and maintainable code structure
- Docker support for easy deployment and execution (Note: Currently limited due to OAuth flow)

## Prerequisites

- Python 3.12 or higher (for local development)
- Docker (for running with Docker, but see limitations below)
- Google Cloud project with Drive API enabled
- Google OAuth 2.0 credentials (not a service account)
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
    *   Configure the OAuth consent screen:
        *   Set the application type to "Desktop app"
        *   Add the necessary scopes (Drive API read-only)
    *   Create OAuth 2.0 credentials:
        *   Choose "Desktop app" as the application type
        *   Download the credentials JSON file
    *   Share the target Drive folder with the Google account you'll use for authentication

4.  **Configure environment variables:**
    Create a `.env` file in the root of the project with the following variables:

    ```env
    # Google Drive settings
    GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
    GOOGLE_OAUTH_CREDENTIALS=path/to/your/oauth_credentials.json
    GOOGLE_TOKEN_CREDENTIALS_LOCATION=token.json  # Optional, defaults to token.json

    # AWS settings
    AWS_ACCESS_KEY_ID=your_aws_access_key
    AWS_SECRET_ACCESS_KEY=your_aws_secret_key
    AWS_REGION=your_aws_region
    S3_BUCKET_NAME=your_bucket_name
    S3_PREFIX=optional/prefix/  # Optional, defaults to empty string

    # Application settings
    RETAIN_FILENAMES=true  # Optional, defaults to true
    ```

    Required variables:
    - `GOOGLE_DRIVE_FOLDER_ID`: The ID of the Google Drive folder containing your images
    - `GOOGLE_OAUTH_CREDENTIALS`: Path to your Google OAuth credentials JSON file
    - `GOOGLE_TOKEN_CREDENTIALS_LOCATION`: Where to save/load the OAuth token. Defaults to `token.json`.
    - `AWS_ACCESS_KEY_ID`: Your AWS access key
    - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
    - `AWS_REGION`: AWS region (e.g., us-east-1)
    - `S3_BUCKET_NAME`: Name of your S3 bucket

    Optional variables:
    - `S3_PREFIX`: Prefix for S3 object keys (default: empty string)
    - `RETAIN_FILENAMES`: Whether to keep original filenames (true) or use sequential numbers (false)

## Usage

### Option 1: Running Locally (Python)

1.  Ensure you have completed the "Local Development Setup" and "Configure environment variables" steps.

2.  Run the application:
    ```bash
    python drive_pictures_to_s3/main.py
    ```

### Option 2: Running with Docker (Currently Limited)

> **Note**: The Docker setup is currently limited because the application uses Google's OAuth flow, which requires user interaction for the initial authentication. This means the first run needs to be done locally to generate the token file. Once you have a valid token file, you can use Docker for subsequent runs.

1.  **Build the Docker image:**
    ```bash
    docker build -t drive-to-s3-importer .
    ```

2.  **Run the Docker container:**
    Make sure you have a `.env` file configured and a valid `token.json` file from a previous local run.
    ```bash
    docker run --rm --env-file .env -v $(pwd)/token.json:/app/token.json drive-to-s3-importer
    ```
    *   `--rm`: Automatically removes the container when it exits.
    *   `--env-file .env`: Loads environment variables from the `.env` file.
    *   `-v $(pwd)/token.json:/app/token.json`: Mounts your local token file into the container.

The script will:
1.  Connect to Google Drive using the service account.
2.  List all images in the specified Drive folder.
3.  Download each image.
4.  Upload it to the configured S3 bucket, applying the chosen naming convention (original or sequential).
5.  Log progress and any errors to the console using `loguru`.

## Configuration Details

Environment variables are loaded from a `.env` file at the root of the project using `pydantic-settings`. The application validates all required variables at startup and provides sensible defaults for optional ones.

Key configuration options:

*   **`GOOGLE_DRIVE_FOLDER_ID`**: The unique identifier of the Google Drive folder from which to fetch images.
*   **`GOOGLE_OAUTH_CREDENTIALS`**: Path to your Google OAuth credentials JSON file. This is used for the initial authentication flow.
*   **`GOOGLE_TOKEN_CREDENTIALS_LOCATION`**: Where to save/load the OAuth token. Defaults to `token.json`.
*   **`S3_BUCKET_NAME`**: The name of your AWS S3 bucket where images will be stored.
*   **`RETAIN_FILENAMES`**: Controls how files are named in S3. `True` keeps original names, `False` uses a sequential numeric prefix (e.g., `1.ext`, `2.ext`).
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