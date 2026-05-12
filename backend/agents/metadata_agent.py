import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class ChallengeAnalysis(BaseModel):
    challenge_id: str
    feature_columns: List[str]
    problem_type: str
    sql_query: str

class AnalysisOutput(BaseModel):
    analyses: List[ChallengeAnalysis]

class DiscoveryOutput(BaseModel):
    relevant_tables: List[str] = Field(description="List of table names identified as potentially relevant to the problem")
    reasoning: str = Field(description="Explanation of why these tables were chosen")

class MetadataAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
            temperature=0
        )

    async def discover_relevant_tables(self, problem_statement: str, challenges: List[str], schema_summary: List[str]) -> DiscoveryOutput:
        """
        Stage 1: High-level table discovery to save tokens.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are an expert Data Architect. Given the problem and challenges, identify which tables are likely to contain the necessary data.\n\n"
            "PROBLEM: {problem_statement}\n"
            "CHALLENGES: {challenges}\n"
            "AVAILABLE TABLES: {tables}\n\n"
            "Return only the table names that are absolutely necessary."
        ).format_messages(
            problem_statement=problem_statement,
            challenges=", ".join(challenges),
            tables=", ".join(schema_summary)
        )
        
        structured_llm = self.llm.with_structured_output(DiscoveryOutput)
        return await structured_llm.ainvoke(prompt)

    async def analyze_columns(self, problem_statement: str, challenges: List[str], user_context: str, detailed_metadata: Dict[str, Any]) -> AnalysisOutput:
        """
        Stage 2: Detailed column analysis incorporating user's specific dataset context.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are a Senior Data Scientist. Analyze the metadata and map features to challenges.\n\n"
            "PROBLEM: {problem_statement}\n"
            "CHALLENGES: {challenges}\n"
            "USER DATASET CONTEXT: {user_context}\n"
            "DETAILED METADATA:\n{metadata}\n\n"
            "Tasks:\n"
            "1. Identify relevant columns for each challenge based on the user's context.\n"
            "2. Generate optimized Databricks SQL.\n"
            "3. Provide reasoning for each feature chosen."
        ).format_messages(
            problem_statement=problem_statement,
            challenges=", ".join(challenges),
            user_context=user_context,
            metadata=json.dumps(detailed_metadata, indent=2)
        )
        
        structured_llm = self.llm.with_structured_output(AnalysisOutput)
        return await structured_llm.ainvoke(prompt)
