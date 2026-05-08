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

class DiscoveryOutput(BaseModel):
    relevant_tables: List[str] = Field(description="List of table names identified as potentially relevant to the problem")
    reasoning: str = Field(description="Explanation of why these tables were chosen")

class MetadataAgent:
    def __init__(self, model_name: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)

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

    async def analyze_columns(self, problem_statement: str, challenges: List[str], detailed_metadata: Dict[str, Any]) -> AnalysisOutput:
        """
        Stage 2: Detailed column analysis and SQL generation for selected tables.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are a Senior Data Scientist. Analyze the detailed column metadata for selected tables and map them to challenges.\n\n"
            "PROBLEM: {problem_statement}\n"
            "CHALLENGES: {challenges}\n"
            "DETAILED METADATA:\n{metadata}\n\n"
            "Generate the SQL and mapping. Problem types must be 'classification' or 'regression'."
        ).format_messages(
            problem_statement=problem_statement,
            challenges=", ".join(challenges),
            metadata=json.dumps(detailed_metadata, indent=2)
        )
        
        structured_llm = self.llm.with_structured_output(AnalysisOutput)
        return await structured_llm.ainvoke(prompt)
