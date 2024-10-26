import os
import io
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from ink2Notes.utils import logger, GOOGLE_CREDS, GOOGLE_TOKEN

# Google Drive API credentials and scopes
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# vérifier l'existence du fichier token
def token_exists(token_path):
    return os.path.exists(token_path)

# Function to get Google credentials with comprehensive handling
def get_google_credentials():
    creds = None
    try:
        # Check if token.json exists to load existing credentials
        if token_exists(GOOGLE_TOKEN):
            creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN, SCOPES)
        # Refresh credentials if they are expired
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Start a new authorization flow if credentials are not available or cannot be refreshed
                flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDS, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the new credentials for next time
            with open(GOOGLE_TOKEN, "w") as token:
                token.write(creds.to_json())
    except Exception as e:
        logger.error("Failed to obtain Google credentials", exc_info=True)
    return creds

# Function to build the Google Drive service
def get_google_service(creds):
    try:
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        logger.error("Failed to build Google Drive service", exc_info=True)
        return None

# Wrappers
def get_media_request(service, file_id):
    return service.files().get_media(fileId=file_id)

def list_files(service, folder_id):
    return service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/'",
        spaces="drive",
        fields="files(id, name)"
    )


# Function to list files in a specific folder in Google Drive
def list_drive_files(service, folder_id):
    try:
        results = list_files(service, folder_id).execute()
        return results.get("files", [])
    except Exception as e:
        logger.error("Failed to list files from Google Drive", exc_info=True)
        return []

def create_downloader(fh, request):
    return MediaIoBaseDownload(fh, request)

# Function to download image content from Google Drive
def download_image(service, file_id, file_name):
    try:
        request = get_media_request(service, file_id)
        fh = io.BytesIO()
        downloader = create_downloader(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            logger.info(f"Downloading {file_name}: {int(status.progress() * 100)}% complete.")
        return fh.getvalue()
    except Exception as e:
        logger.error(f"Failed to download file {file_name}", exc_info=True)
        return None


# Function to get image files from Google Drive folder
def get_image_files(folder_id="your_folder_id_here"):
    creds = get_google_credentials()
    if not creds:
        logger.error("No valid Google credentials available.")
        return []

    service = get_google_service(creds)
    if not service:
        logger.error("Failed to create Google Drive service.")
        return []

    files = list_drive_files(service, folder_id)
    if not files:
        logger.info("No image files found in the specified Google Drive folder.")
        return []

    image_files = []
    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        file_data = download_image(service, file_id, file_name)
        if file_data:
            image_files.append({"name": file_name, "data": file_data})

    return image_files
