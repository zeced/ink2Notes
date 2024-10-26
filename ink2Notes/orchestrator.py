# ink2Notes/orchestrator.py
import asyncio
import datetime
from ink2Notes.drive_connector import get_image_files
from ink2Notes.openai_connector import analyze_image
from ink2Notes.notion_connector import create_notion_page
from ink2Notes.utils import logger, GOOGLE_DRIVE_FOLDER_ID

async def process_image(image):
    """Process a single image: analyze and create a Notion page with the extracted data."""
    image_name = image["name"]
    image_data = image["data"]

    # Analyze the image with OpenAI
    logger.info(f"Starting analysis for {image_name}")
    analysis_result = await asyncio.to_thread(analyze_image, image_data)
    if analysis_result is None:
        logger.error(f"Failed to analyze image {image_name}")
        return

    # Define properties for the Notion page
    title = image_name.split(".")[0]  # Use filename as title
    tags = ["Scanned", "Notes"]  # Example tags; you may adjust based on the context
    added_on = datetime.date.today().isoformat()  # Current date as 'Ajouté le'

    # Create the page in Notion
    logger.info(f"Creating Notion page for {image_name}")
    notion_response = await asyncio.to_thread(create_notion_page, title, tags, added_on, analysis_result)
    if notion_response is None:
        logger.error(f"Failed to create Notion page for {image_name}")
        return

    logger.info(f"Successfully processed and added {image_name} to Notion")

async def orchestrate():
    """Main function to orchestrate the process of fetching images, analyzing them, and uploading to Notion."""
    # Step 1: Get all image files from Google Drive
    logger.info("Fetching image files from Google Drive")
    image_files = await asyncio.to_thread(get_image_files, GOOGLE_DRIVE_FOLDER_ID)
    if not image_files:
        logger.warning("No images found in Google Drive or failed to fetch images.")
        return

    # Step 2: Process each image concurrently
    tasks = [process_image(image) for image in image_files]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(orchestrate())
