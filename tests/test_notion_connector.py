# tests/test_notion_connector.py
import pytest
from unittest.mock import patch
from ink2Notes.notion_connector import create_notion_page

@patch("ink2Notes.notion_connector.notion.pages.create")
def test_create_notion_page(mock_create):
    # Mock Notion API response
    mock_create.return_value = {"id": "mock_page_id"}

    # Call function
    response = create_notion_page("Test Title", ["Tag1", "Tag2"], "2024-10-22", "This is some content")
    assert response["id"] == "mock_page_id"
