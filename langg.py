from pydantic import BaseModel, Field
from typing import TypedDict, List
import enum
import json
import datetime
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END


# gemini client
from google import genai
client = genai.Client()


# schemas
class Team(enum.Enum):
    EVENTS = "EVENTS"
    MARKETING = "MARKETING"
    NONE = "NONE"
class Deliverable(BaseModel):
    name: str = Field(description="A short, descriptive name for the deliverable, e.g., 'Branded Booth'.")
    description: str = Field(description="The full description of the deliverable from the contract.")
    assigned_team: Team = Field(description="The internal team responsible. Must be 'EVENTS' or 'MARKETING'.")
    due_date: datetime.datetime = Field(description="The due date for the deliverable, if mentioned. Format as YYYY-MM-DD.")

# state schema for langgraph
class GraphState(TypedDict):
    contract_text: str # input
    raw_deliverables: List[Deliverable] # intermediate output
    processed_tasks: str # final output

# Let's assume that below is the output of PDF parser (unstructured text)
sample_contract_text = """
    As part of the package, the client will receive one branded booth at the conference,
    three dedicated social media posts on X and LinkedIn, and a featured placement on
    the website. All marketing deliverables must be completed before the 1st of December
    2025.
"""

# node 1: str -> List[Deliverable]
def extract_deliverables_node(state):
    print("---NODE 1: EXTRACTING DELIVERABLES---")
    contract_text = state['contract_text']

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Here is the contract text: " + contract_text + ". List the name of tasks specified along with their descriptions",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Deliverable],
        },
    )

    return {"raw_deliverables": response.parsed}

# node 2: List[Deliverable] -> JSON
def parse_deliverables_node(state):
    print("---NODE: PARSING DELIVERABLES TO JSON---")
    raw_deliverables = state['raw_deliverables']
    tasks = []

    for deliverable in raw_deliverables:
        task = {
            "name": deliverable.name,
            "description": deliverable.description,
            "team": deliverable.assigned_team.value,
            # Format the datetime object into a string
            "due_date": deliverable.due_date.strftime("%b %d, %Y") if deliverable.due_date else "N/A"
        }
        tasks.append(task)

    return {"processed_tasks": json.dumps(tasks, indent=2)}


# monday.com listener
def monday_listener():
    workflow = StateGraph(GraphState)

    workflow.add_node("extract", extract_deliverables_node)
    workflow.add_node("parse", parse_deliverables_node)

    workflow.set_entry_point("extract")
    workflow.add_edge("extract", "parse")
    workflow.add_edge("parse", END)

    app = workflow.compile()

    inputs = {"contract_text": sample_contract_text}

    final_state = app.invoke(inputs)

    print("\n---FINAL OUTPUT---")
    print(final_state['processed_tasks'])


if __name__ == "__main__":
    monday_listener()
