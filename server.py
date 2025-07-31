import enum
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

from dotenv import load_dotenv
load_dotenv()

from google import genai

# Configure the FastAPI app
app = FastAPI(
    title="Deliverable Extraction API",
    description="Extracts structured deliverables from unstructured text using Google Gemini.",
    version="1.0.0",
)

# Configure the Gemini client
try:
    client = genai.Client()
except Exception as e:
    raise RuntimeError(f"Failed to initialize Gemini client. Check your GOOGLE_API_KEY. Error: {e}")

# schemas
class Team(str, enum.Enum):
    EVENTS = "EVENTS"
    MARKETING = "MARKETING"
    NONE = "NONE"
class Deliverable(BaseModel):
    name: str = Field(description="A short, descriptive name for the deliverable, e.g., 'Branded Booth'.")
    description: str = Field(description="The full description of the deliverable from the contract.")
    assigned_team: Team = Field(description="The internal team responsible. Must be one of the enum values.")
    due_date: datetime | None = Field(
        default=None,
        description="The due date for the deliverable. Format as YYYY-MM-DD. Can be null if not mentioned."
    )
class WebhookPayload(BaseModel):
    text: str = Field(description="The unstructured text from the source (e.g., monday.com update, HubSpot note).")


async def process_deliverables(contract_text: str) -> List[Deliverable]:
    prompt = f"""
    Analyze the following contract text and extract all specified tasks or deliverables.
    For each deliverable, provide its name, a detailed description, the responsible team, and the due date if mentioned.

    Contract Text:
    ---
    {contract_text}
    ---
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[Deliverable],
            },
        )
        return response.parsed

    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process text with the generative AI model."
        )


# toy listener for monday.com webhook
@app.post("/webhook/monday", response_model=List[Deliverable])
async def trigger_from_monday(payload: WebhookPayload):
    print("Received trigger from Monday.com")
    deliverables = await process_deliverables(payload.text)
    return deliverables

# toy listener for hubspot.com webhook
@app.post("/webhook/hubspot", response_model=List[Deliverable])
async def trigger_from_hubspot(payload: WebhookPayload):
    print("Received trigger from HubSpot")
    deliverables = await process_deliverables(payload.text)
    return deliverables

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Deliverable Extraction API is running."}
