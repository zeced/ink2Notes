# ink2Notes/openai_connector.py
import base64
from openai import OpenAI
from ink2Notes.utils import OPENAI_API_KEY, logger

client = OpenAI(api_key=OPENAI_API_KEY)

# Function to encode the image to base64
def encode_image(image_data):
    return base64.b64encode(image_data).decode("utf-8")

def analyze_image(image_data):
    try:
        logger.info(f"Analyzing image with OpenAI Vision API...")

        # Encode the image to base64
        base64_image = encode_image(image_data)

        # Prepare the prompt (text request) for OpenAI
        prompt = f"Extract the handwritten text and convert any diagrams in the image to MermaidJS format."

        # Send the image and prompt to OpenAI's GPT-4 Vision API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
        )

        logger.info(f"Analysis completed.")

        # Extract the response content
        return response.choices[0].message.content
    except Exception as e:
        logger.error("An error occurred during image analysis with OpenAI", exc_info=True)
        return None
