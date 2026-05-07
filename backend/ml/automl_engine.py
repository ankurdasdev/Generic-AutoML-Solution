import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
import mlflow
import joblib
import os

class AutoMLCompetition:
    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)

    def train_challenge(self, df: pd.DataFrame, target_col: str, problem_type: str) -> str:
        """
        Runs competition between models and returns the champion model path.
        """
        X = df.drop(columns=[target_col])
        y = df[target_col]

        # Basic preprocessing (Handling categoricals for the generic solution)
        X = pd.get_dummies(X)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        models = self._get_model_candidates(problem_type)
        best_model = None
        best_score = -np.inf if problem_type == "classification" else np.inf
        champion_run_id = None

        for name, model in models.items():
            with mlflow.start_run(run_name=name) as run:
                model.fit(X_train, y_train)
                
                # Evaluation
                if problem_type == "classification":
                    y_pred = model.predict(X_test)
                    score = f1_score(y_test, y_pred, average='weighted')
                    mlflow.log_metric("f1_weighted", score)
                    mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
                    if score > best_score:
                        best_score = score
                        best_model = model
                        champion_run_id = run.info.run_id
                else:
                    y_pred = model.predict(X_test)
                    score = mean_squared_error(y_test, y_pred)
                    mlflow.log_metric("mse", score)
                    mlflow.log_metric("r2", r2_score(y_test, y_pred))
                    if score < best_score:
                        best_score = score
                        best_model = model
                        champion_run_id = run.info.run_id
                
                mlflow.sklearn.log_model(model, "model")
                mlflow.log_param("problem_type", problem_type)

        # Register Champion
        if best_model:
            model_path = f"backend/models/champion_{self.experiment_name}.joblib"
            os.makedirs("backend/models", exist_ok=True)
            joblib.dump(best_model, model_path)
            print(f"Champion for {self.experiment_name} is {best_model.__class__.__name__} with score {best_score}")
            return model_path
        
        return ""

    def _get_model_candidates(self, problem_type: str) -> Dict[str, Any]:
        if problem_type == "classification":
            return {
                "RandomForest": RandomForestClassifier(n_estimators=100),
                "XGBoost": XGBClassifier(),
                "LightGBM": LGBMClassifier(),
                "LogisticRegression": LogisticRegression(max_iter=1000)
            }
        else:
            return {
                "RandomForest": RandomForestRegressor(n_estimators=100),
                "XGBoost": XGBRegressor(),
                "LightGBM": LGBMRegressor(),
                "LinearRegression": LinearRegression()
            }
