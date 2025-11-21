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
    def anthropic_analyze_image(image_url: str) -> str:
        """Analyze the content of the image file and returns an structured output."""

        # Run inference
        model = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
        )

        input_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": f"""You are going to receive 3 types of documents in spanish:
                - 1. Cedula de ciudadania. Extract all the needed information form the image.
                - 2. Certificado laboral. Find the person's salary (salario).
                - 3. Colilla de pago. Find any deductions that the person may have from the salary.
                """},
                {"type": "image", "url": image_url},
            ],
        }
        response = model.invoke([input_message])
        return response

    @tool
    def compare_documents(payload: str) -> str:
        """Compare the payload and call the API to compare person's details."""
        request = requests.get(
            f"https://credifast-api.harnonlabs.workers.dev/api/get-lead?leadID=406a65ff-fd52-4384-8424-d25d225429ff",
            json=payload,
        )
        return request.json()

    TOOLS = [anthropic_analyze_image, compare_documents]
    TOOLS_BY_NAME = {t.name: t for t in TOOLS}

    # Model used inside the agentic loop (tool-calling)
    model_with_tools = model.bind_tools(TOOLS)

    return model_with_tools, TOOLS_BY_NAME