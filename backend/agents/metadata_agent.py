import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class ChallengeAnalysis(BaseModel):
    challenge_id: str
    identified_columns: List[str] = Field(description="List of columns needed for this challenge")
    sql_query: str = Field(description="SQL query to fetch these columns from the data lake")
    problem_type: str = Field(description="classification or regression")
    reasoning: str = Field(description="Brief explanation of why these columns were chosen")

class AnalysisOutput(BaseModel):
    analyses: List[ChallengeAnalysis]

class MetadataAgent:
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.parser = ChatPromptTemplate.from_template(
            "You are a Senior Data Scientist and AutoML Expert.\n"
            "Analyze the following organization metadata and problem statement to identify the features needed for each challenge.\n\n"
            "PROBLEM STATEMENT:\n{problem_statement}\n\n"
            "CHALLENGES:\n{challenges}\n\n"
            "ORG METADATA (JSON SCHEMA):\n{metadata}\n\n"
            "For each challenge, identify relevant tables/columns and write a SQL query for Databricks.\n"
            "The query should select the necessary features. DO NOT include the target column as it will be labeled later.\n"
            "Decide if the challenge is a classification or regression problem."
        )

    async def analyze(self, problem_statement: str, challenges: List[str], metadata: Dict[str, Any]) -> AnalysisOutput:
        prompt = self.parser.format_messages(
            problem_statement=problem_statement,
            challenges=", ".join(challenges),
            metadata=json.dumps(metadata, indent=2)
        )
        
        # We use a structured output approach
        structured_llm = self.llm.with_structured_output(AnalysisOutput)
        response = await structured_llm.ainvoke(prompt)
        return response
