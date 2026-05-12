import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os

class DraftResponse(BaseModel):
    ai_message: str = Field(description="The response message to show in the chat bubble.")
    problem_statement: str = Field(description="The current refined problem statement.")
    challenges: List[str] = Field(description="The list of identified ML challenges.")
    phase: str = Field(description="The current phase: 'problem' or 'challenges'.")

class DrafterAgent:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.2,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    async def discuss(self, history: List[Dict[str, str]], current_input: str) -> DraftResponse:
        """
        Two-phase discussion logic: 
        1. Problem Statement refinement.
        2. Challenge extraction.
        """
        prompt = ChatPromptTemplate.from_template(
            "You are an Expert AI Business Analyst. Your goal is to help a user draft a 'Problem Statement' and 'ML Challenges'.\n\n"
            "PHASE LOGIC:\n"
            "- Phase 1 (Problem): Focus ONLY on understanding the core business goal. Draft a clear problem statement.\n"
            "- Phase 2 (Challenges): Once the problem is clear, suggest 2-3 specific technical challenges to solve.\n\n"
            "CONVERSATION HISTORY:\n{history}\n"
            "USER INPUT: {current_input}\n\n"
            "INSTRUCTIONS:\n"
            "- Be concise and professional.\n"
            "- If the problem is not clear, stay in Phase 1.\n"
            "- If the user provides a problem, move to Phase 2.\n"
            "- Always return valid JSON matching the structure."
        ).format_messages(
            history=json.dumps(history, indent=2),
            current_input=current_input
        )

        structured_llm = self.llm.with_structured_output(DraftResponse)
        return await structured_llm.ainvoke(prompt)
