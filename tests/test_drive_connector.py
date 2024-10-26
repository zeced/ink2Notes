import pytest
from unittest.mock import patch, MagicMock
import io
from ink2Notes.drive_connector import get_google_credentials, get_google_service, list_drive_files, download_image, get_image_files
from ink2Notes.utils import GOOGLE_TOKEN

# Test get_google_credentials

@patch("ink2Notes.drive_connector.token_exists")
@patch("ink2Notes.drive_connector.Credentials.from_authorized_user_file")
def test_get_google_credentials(mock_creds_from_file, mock_token_exists):
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds_from_file.return_value = mock_creds
    mock_token_exists.return_value = True

    creds = get_google_credentials()
    assert creds == mock_creds
    mock_creds_from_file.assert_called_once_with(GOOGLE_TOKEN, ["https://www.googleapis.com/auth/drive.readonly"])

# Test get_google_service
@patch("ink2Notes.drive_connector.build")
def test_get_google_service(mock_build):
    mock_creds = MagicMock()
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    service = get_google_service(mock_creds)
    assert service == mock_service
    mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)

# Test list_drive_files
@patch("ink2Notes.drive_connector.get_google_service")
def test_list_drive_files(mock_get_service):
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service
    mock_service.files.return_value.list.return_value.execute.return_value = {"files": [{"id": "file1", "name": "image1.jpg"}]}

    files = list_drive_files(mock_service, "folder_id")
    assert len(files) == 1
    assert files[0]["name"] == "image1.jpg"
    mock_service.files.return_value.list.assert_called_once_with(
        q="'folder_id' in parents and mimeType contains 'image/'",
        spaces="drive",
        fields="files(id, name)"
    )

# Test download_image
@patch("ink2Notes.drive_connector.create_downloader")
@patch("ink2Notes.drive_connector.get_media_request")
def test_download_image(mock_get_media, mock_create_downloader):
    mock_service = MagicMock()
    mock_request = MagicMock()
    mock_get_media.return_value = mock_request

    mock_downloader = MagicMock()
    mock_create_downloader.return_value = mock_downloader

    # Remplacer la simulation de la méthode `progress`
    mock_status = MagicMock()
    mock_status.progress.return_value = 1.0
    mock_downloader.next_chunk.side_effect = [(mock_status, True)]

    file_data = download_image(mock_service, "file_id", "file_name.jpg")
    assert file_data is not None
    mock_get_media.assert_called_once_with(mock_service, "file_id")
    mock_create_downloader.assert_called_once()
    assert isinstance(mock_create_downloader.call_args[0][0], io.BytesIO)
    assert mock_create_downloader.call_args[0][1] == mock_request


@patch("ink2Notes.drive_connector.list_files")
@patch("ink2Notes.drive_connector.get_google_service")
@patch("ink2Notes.drive_connector.get_google_credentials")
@patch("ink2Notes.drive_connector.download_image")
def test_get_image_files(mock_download_image, mock_get_credentials, mock_get_service, mock_list_files):
    mock_creds = MagicMock()
    mock_get_credentials.return_value = mock_creds

    mock_service = MagicMock()
    mock_get_service.return_value = mock_service

    mock_list_files.return_value.execute.return_value = {"files": [{"id": "file1", "name": "image1.jpg"}]}
    mock_download_image.return_value = b"image data"

    files = get_image_files("folder_id")
    assert len(files) == 1
    assert files[0]["name"] == "image1.jpg"
    assert files[0]["data"] == b"image data"
    mock_get_credentials.assert_called_once()
    mock_get_service.assert_called_once_with(mock_creds)
    mock_list_files.assert_called_once_with(mock_service, "folder_id")
    mock_download_image.assert_called_once_with(mock_service, "file1", "image1.jpg")
