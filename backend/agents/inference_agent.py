import os
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from typing import List, Dict, Any

class InferenceAgent:
    def __init__(self, tool_registry: Any):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
            temperature=0
        )
        self.tool_registry = tool_registry
        
        # Define the system prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a highly intelligent business assistant. "
                       "You have access to specific predictive micro-models (tools). "
                       "When a user asks a question, identify the relevant challenge, "
                       "call the corresponding tool, and synthesize a helpful business response."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def get_agent_executor(self) -> AgentExecutor:
        # Dynamically create LangChain tools from our MCP registry
        langchain_tools = []
        for tool_def in self.tool_registry.get_tool_definitions():
            
            # Use a closure to capture the tool_name
            def create_tool_fn(t_name):
                @tool(t_name)
                def dynamic_tool(data: List[Dict[str, Any]]) -> Dict[str, Any]:
                    """Predict using the specified micro-model."""
                    return self.tool_registry.execute_tool(t_name, data)
                return dynamic_tool
            
            langchain_tools.append(create_tool_fn(tool_def["name"]))

        agent = create_openai_functions_agent(self.llm, langchain_tools, self.prompt)
        return AgentExecutor(agent=agent, tools=langchain_tools, verbose=True)

    async def answer_question(self, user_question: str) -> str:
        executor = self.get_agent_executor()
        response = await executor.ainvoke({"input": user_question})
        return response["output"]
