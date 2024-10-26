# ink2Notes/notion_connector.py
from notion_client import Client
from ink2Notes.utils import NOTION_API_KEY, NOTION_DATABASE_ID, logger

notion = Client(auth=NOTION_API_KEY)

def create_notion_page(title, tags, added_on, content):
    try:
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Titre": {"title": [{"text": {"content": title}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in tags]},
                "Ajout": {"date": {"start": added_on}}
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": content}}]
                    }
                }
            ]
        )
        return response
    except Exception as e:
        logger.error("An error occurred while creating a Notion page", exc_info=True)
        return None
