import joblib
import pandas as pd
from typing import Dict, Any, List, Callable
import json

class MCPToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_challenge_tool(self, challenge_id: str, model_path: str, feature_cols: List[str]):
        """
        Registers a trained micro-model as an MCP tool.
        """
        model = joblib.load(model_path)
        
        self.tools[challenge_id] = {
            "name": f"predict_{challenge_id.lower()}",
            "description": f"Predicts outcome for challenge {challenge_id}",
            "model": model,
            "feature_cols": feature_cols,
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of records (JSON) to predict"
                    }
                },
                "required": ["data"]
            }
        }
        print(f"Registered MCP Tool: predict_{challenge_id.lower()}")

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for tool in self.tools.values()
        ]

    def execute_tool(self, tool_name: str, data_json: List[Dict[str, Any]]) -> Dict[str, Any]:
        challenge_id = tool_name.replace("predict_", "").upper()
        if challenge_id not in self.tools:
            return {"error": f"Tool {tool_name} not found"}

        tool = self.tools[challenge_id]
        model = tool["model"]
        feature_cols = tool["feature_cols"]

        # Prepare data for inference
        df = pd.DataFrame(data_json)
        
        # Ensure only relevant feature columns are used
        # (Handling missing columns with 0 for robustness)
        X = pd.DataFrame(index=df.index, columns=feature_cols).fillna(0)
        for col in feature_cols:
            if col in df.columns:
                X[col] = df[col]

        # One-hot encoding might be needed if trained that way
        # For simplicity, we assume numeric features or handling in model pipeline
        # (Better: Save a scikit-learn Pipeline with Scaler/Encoder)
        
        predictions = model.predict(X)
        probabilities = []
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X).tolist()

        return {
            "challenge_id": challenge_id,
            "predictions": predictions.tolist(),
            "probabilities": probabilities,
            "status": "success"
        }
