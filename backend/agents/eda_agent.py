import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class FeatureProposal(BaseModel):
    feature_name: str
    description: str
    logic: str
    reasoning: str

class EDAPlan(BaseModel):
    proposals: List[FeatureProposal]
    summary: str

class EDAAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
            temperature=0.1
        )

    async def suggest_features(self, problem_statement: str, objects: List[str], sample_metadata: Dict[str, Any]) -> EDAPlan:
        """
        Generates initial EDA and Feature Engineering suggestions.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are an expert Data Scientist. Propose 5 high-impact feature engineering steps and EDA tasks for this problem.\n\n"
            "PROBLEM: {problem_statement}\n"
            "OBJECTS: {objects}\n"
            "METADATA: {metadata}\n\n"
            "Focus on domain-specific features (e.g., velocity, ratios, seasonal trends)."
        ).format_messages(
            problem_statement=problem_statement,
            objects=", ".join(objects),
            metadata=json.dumps(sample_metadata)
        )
        
        structured_llm = self.llm.with_structured_output(EDAPlan)
        return await structured_llm.ainvoke(prompt)

    async def refine_plan(self, current_plan: EDAPlan, user_feedback: str) -> EDAPlan:
        """
        Updates the plan based on user enhancements.
        """
        prompt = ChatPromptTemplate.from_template(
            "Refine the current EDA/FE plan based on user feedback.\n\n"
            "CURRENT PLAN: {plan}\n"
            "USER FEEDBACK: {feedback}\n\n"
            "Update the proposals list accordingly."
        ).format_messages(
            plan=current_plan.json(),
            feedback=user_feedback
        )
        
        structured_llm = self.llm.with_structured_output(EDAPlan)
        return await structured_llm.ainvoke(prompt)
