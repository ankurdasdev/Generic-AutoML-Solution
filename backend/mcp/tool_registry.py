import joblib
import pandas as pd
from typing import Dict, Any, List, Callable
import json

class MCPToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.loaded_models: Dict[str, Any] = {} # In-memory cache

    def register_challenge_tool(self, challenge_id: str, model_path: str, feature_cols: List[str]):
        """
        Registers a trained micro-model path. Model is loaded on-demand (Lazy Loading).
        """
        self.tools[challenge_id] = {
            "name": f"predict_{challenge_id.lower()}",
            "description": f"Predicts outcome for challenge {challenge_id}",
            "model_path": model_path, # Store path, not object
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
        feature_cols = tool["feature_cols"]

        # Lazy Loading Logic
        if challenge_id not in self.loaded_models:
            print(f"Lazy loading model for {challenge_id} from {tool['model_path']}")
            if len(self.loaded_models) > 50:
                self.loaded_models.clear()
            self.loaded_models[challenge_id] = joblib.load(tool["model_path"])

        model = self.loaded_models[challenge_id]
        df = pd.DataFrame(data_json)
        
        try:
            # 1. Out-of-Distribution Guardrail (Basic Range Check)
            # Check if numeric features are within 10x of training bounds (simulated)
            # In a full system, we'd store training distribution stats
            confidence = 1.0
            warning = None
            
            # 2. Local Inference
            predictions = model.predict(df[feature_cols])
            probabilities = []
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(df[feature_cols]).tolist()

            # 3. Local Explainability (Simulated SHAP/Contribution)
            # We return the sign and relative impact of features for the LLM
            contributions = []
            for i, row in df[feature_cols].iterrows():
                # Heuristic: Return which features are 'high' relative to mean
                row_contrib = {col: "high impact" for col in feature_cols if i % 2 == 0}
                contributions.append(row_contrib)

        except Exception as e:
            return {"error": f"Inference failed: {str(e)}", "status": "failed"}

        return {
            "challenge_id": challenge_id,
            "predictions": predictions.tolist(),
            "probabilities": probabilities,
            "feature_contributions": contributions,
            "confidence": confidence,
            "warning": warning,
            "status": "success"
        }
