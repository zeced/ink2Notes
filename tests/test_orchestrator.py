# tests/test_orchestrator.py
import pytest
from unittest.mock import patch, AsyncMock, ANY
from ink2Notes.orchestrator import orchestrate

@patch("ink2Notes.orchestrator.get_image_files", return_value=[{"name": "image1.jpg", "data": b"image data"}])
@patch("ink2Notes.orchestrator.analyze_image", return_value="Extracted text")
@patch("ink2Notes.orchestrator.create_notion_page", return_value={"id": "mock_page_id"})
@pytest.mark.asyncio
async def test_orchestrate(mock_create_page, mock_analyze, mock_get_images):
    # Run the orchestrator
    await orchestrate()

    # Print debug output to inspect each mock call
    print("mock_get_images calls:", mock_get_images.call_args_list)
    print("mock_analyze calls:", mock_analyze.call_args_list)
    print("mock_create_page calls:", mock_create_page.call_args_list)

    # Verify each function was called as expected
    mock_get_images.assert_called_once()
    mock_analyze.assert_called_once_with(b"image data")
    mock_create_page.assert_called_once_with(
        "image1",  # Title
        ["Scanned", "Notes"],  # Tags
        ANY,  # Date added (allowing any date)
        "Extracted text"  # Content from OpenAI
    )
