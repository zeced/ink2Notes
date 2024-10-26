# tests/test_openai_connector.py
import pytest
from unittest.mock import patch, MagicMock
from ink2Notes.openai_connector import analyze_image

@patch("ink2Notes.openai_connector.client.chat.completions.create")
def test_analyze_image(mock_create):
    # Mock OpenAI API response
    mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Extracted text"))])

    # Call function
    result = analyze_image(b"image data")
    assert result == "Extracted text"
