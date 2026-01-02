from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.chat_models import init_chat_model
import requests
def get_model():
    # Base chat model (you can swap this model ID)
    model = init_chat_model(
        "claude-sonnet-4-5-20250929",
        temperature=0,
    )

    @tool
    def analyze_image_ocr(image_url: str) -> str:
        """Perform OCR and extract key information by document type."""

        # Run inference
        model = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
        )

        input_message = {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "Perform OCR and extract key information by document type. Do not infer data that is not clearly visible."
                },
                {"type": "image", "url": image_url},
            ],
        }
        response = model.invoke([input_message])
        return response

    @tool
    def get_data_from_api(payload: str) -> str:
        """Get the data from the API to compare with the information from the images."""
        request = requests.get(
            f"https://credifast-api.harnonlabs.workers.dev/api/get-lead?leadID=406a65ff-fd52-4384-8424-d25d225429ff",
            json=payload,
        )
        return request.json()

    TOOLS = [analyze_image_ocr, get_data_from_api]
    TOOLS_BY_NAME = {t.name: t for t in TOOLS}

    # Model used inside the agentic loop (tool-calling)
    model_with_tools = model.bind_tools(TOOLS)

    return model_with_tools, TOOLS_BY_NAME