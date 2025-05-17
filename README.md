# Drive Pictures to S3

A Python application that transfers images from a Google Drive folder to AWS S3, with options to retain original filenames or use sequential numbering.

## Features

- Transfer images from Google Drive to AWS S3
- Configurable file naming (original names or sequential numbers)
- Comprehensive error handling and logging
- Environment-based configuration
- Modular and maintainable code structure

## Prerequisites

- Python 3.8 or higher
- Google Cloud project with Drive API enabled
- Google service account with access to the target Drive folder
- AWS account with S3 access
- AWS credentials with appropriate permissions

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd drive-pictures-to-s3
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google Cloud:
   - Create a project in Google Cloud Console
   - Enable the Google Drive API
   - Create a service account
   - Download the service account key file
   - Share the target Drive folder with the service account email

5. Configure environment variables:
   - Copy `example.env` to `.env`
   - Fill in the required values:
     - Google Drive settings
     - AWS credentials
     - Application settings

## Usage

Run the application:
```bash
python -m src.main
```

The script will:
1. Connect to Google Drive using the service account
2. List all images in the specified folder
3. Download each image
4. Upload to S3 with either original names or sequential numbers
5. Log progress and any errors

## Configuration

### Environment Variables

- `GOOGLE_DRIVE_FOLDER_ID`: ID of the Google Drive folder to process
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google service account credentials file
- `AWS_ACCESS_KEY_ID`: AWS access key ID
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key
- `AWS_REGION`: AWS region
- `S3_BUCKET_NAME`: S3 bucket name
- `S3_PREFIX`: Optional prefix for S3 object keys
- `RETAIN_FILENAMES`: Whether to retain original filenames (true) or use sequential numbers (false)

## Error Handling

The application includes comprehensive error handling:
- Individual file processing errors are logged but don't stop the entire process
- Critical errors (e.g., authentication failures) will stop the process
- All errors are logged with appropriate context

## Logging

Logs are written to stdout with the following format:
```
YYYY-MM-DD HH:MM:SS,SSS - module_name - LEVEL - message
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 