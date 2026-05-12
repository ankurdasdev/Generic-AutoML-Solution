from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from services.data_fetcher import SalesforceFetcher
from agents.metadata_agent import MetadataAgent
from agents.drafter_agent import DrafterAgent

load_dotenv()

app = FastAPI(title="Generic AutoML Solution API")

class DiscussionRequest(BaseModel):
    history: List[Dict[str, str]]
    user_input: str

@app.post("/training/discuss")
async def discuss_problem(request: DiscussionRequest):
    """
    Step 1: AI Agent discusses the problem statement and challenges with the user.
    """
    agent = DrafterAgent()
    result = await agent.discuss(request.history, request.user_input)
    return result

# Configure CORS for premium frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChallengeRequest(BaseModel):
    problem_statement: str
    challenges: List[str]
    connector_config: Dict[str, Any]
    org_metadata: Dict[str, Any]  # JSON Schema of all tables

@app.get("/")
async def root():
    return {"message": "AutoML Backend is running", "status": "premium"}

@app.get("/org/schema-summary")
async def get_schema_summary():
    """
    Fetches a high-level list of available objects from the connected org.
    """
    fetcher = SalesforceFetcher()
    objects = fetcher.get_global_metadata()
    if not objects:
        # Fallback for demo if no credentials provided
        return {"objects": ["Account", "Opportunity", "Contact", "Lead", "Task", "OpportunityHistory"]}
    return {"objects": objects}

@app.post("/training/discover-objects")
async def discover_objects(request: ChallengeRequest):
    """
    Step 3: AI Agent identifies relevant objects based on problem statement and live schema.
    """
    fetcher = SalesforceFetcher()
    schema_summary = fetcher.get_global_metadata()
    if not schema_summary:
        schema_summary = ["Account", "Opportunity", "Lead", "OpportunityHistory"]

    agent = MetadataAgent()
    result = await agent.discover_relevant_tables(
        problem_statement=request.problem_statement,
        challenges=request.challenges,
        schema_summary=schema_summary
    )
    return result

@app.post("/training/generate-sheets")
async def generate_sheets(dataset_cols: Dict[str, List[str]], sql_queries: Dict[str, str]):
    """
    Part 2: Run queries on Databricks and generate multi-sheet Excel.
    """
    # TODO: Implement Databricks execution and Excel generation
    return {"message": "Sheets generated", "download_url": "/data/labeled/training_data.xlsx"}

@app.post("/training/start-automl")
async def start_automl(file: UploadFile = File(...)):
    """
    Part 4: Run AutoML competition and register models in MLFlow.
    """
    # TODO: Implement Custom ML Competition Loop
    return {"message": "Training started", "job_id": "job_123"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
