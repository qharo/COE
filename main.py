
from pydantic import BaseModel, Field
import enum
import json
import datetime
from dotenv import load_dotenv
load_dotenv()

from google import genai

# configure gemini
client = genai.Client()


# define output types (schemas)
class Team(enum.Enum):
    EVENTS = "EVENTS"
    MARKETING = "MARKETING"
    NONE = "NONE"
class Deliverable(BaseModel):
    name: str = Field(description="A short, descriptive name for the deliverable, e.g., 'Branded Booth'.")
    description: str = Field(description="The full description of the deliverable from the contract.")
    assigned_team: Team = Field(description="The internal team responsible. Must be 'Events Team' or 'Marketing Team'.")
    due_date: datetime.datetime = Field(description="The due date for the deliverable, if mentioned. Format as YYYY-MM-DD if possible.")

# let's assume that below is the output of PDF parser (unstructured text)
sample_contract_text = """
    As part of the package, the client will receive one branded booth at the conference,
    three dedicated social media posts on X and LinkedIn, and a featured placement on
    the website. All marketing deliverables must be completed before the 1st of December
    2025.

    Deliverable Description
    Booth 9sqm Branded booth at the conference
    Three (3) social media posts on X and
    LinkedIn

    Share and mention the client on social
    media

    Featured placement on the website Add the client logo on the website in the"""

# assuming just the text is provided
sample_contract_text2 = """
As part of the package, the client will receive one branded booth at the conference,
three dedicated social media posts on X and LinkedIn, and a featured placement on
the website. All marketing deliverables must be completed before the 1st of December
2025.
"""

# extract raw deliverables
def process_deliverables(contract_text):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Here is the contract text: " + contract_text + ". List the name of tasks specified along with their descriptions",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Deliverable],
        },
    )

    # we'll convert it to JSON as requested
    parsed_response = response.parsed

    tasks = []

    for deliverable in parsed_response:
        task = {
            "name": deliverable.name,
            "description": deliverable.description,
            "team": deliverable.assigned_team.value,
            "due_date": deliverable.due_date.date().strftime("%b %d, %Y")
        }
        tasks.append(task)

    return json.dumps(tasks)


# Monday.com listener
def monday_listener():
    contract_text = sample_contract_text2
    output =process_deliverables(contract_text)

    print(output)

if __name__ == "__main__":
    # assume monday.com is triggered
    monday_listener()
