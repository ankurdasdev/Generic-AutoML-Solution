import pandas as pd
import xlsxwriter
from typing import Dict, List, Any
import os

class DataProcessor:
    def __init__(self, output_dir: str = "backend/data/labeled"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run_queries_and_save(self, queries: Dict[str, str], connector: Any) -> str:
        """
        Executes queries for each challenge and saves to a multi-sheet Excel.
        """
        file_path = os.path.join(self.output_dir, "training_data_template.xlsx")
        writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

        for challenge_id, query in queries.items():
            # Execute query via connector (Databricks / Mock)
            df = connector.execute_query(query)
            
            # Add Target column
            df['Target'] = "" # Empty for human labeling
            
            # Write to sheet
            df.to_excel(writer, sheet_name=challenge_id, index=False)
            
            # Optional: Add formatting to highlight the Target column
            workbook = writer.book
            worksheet = writer.sheets[challenge_id]
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
            target_format = workbook.add_format({'bg_color': '#FFC7CE', 'border': 1})
            
            # Format the 'Target' column (last column)
            target_col_idx = len(df.columns) - 1
            worksheet.set_column(target_col_idx, target_col_idx, 15, target_format)

        writer.close()
        return file_path

class MockConnector:
    """Mock connector for initial development"""
    def execute_query(self, query: str) -> pd.DataFrame:
        # Generate some dummy data based on query (very basic)
        return pd.DataFrame({
            "feature_1": [1.0, 2.0, 3.0],
            "feature_2": [0.5, 1.5, 2.5],
            "feature_3": ["A", "B", "A"]
        })

class DatabricksConnector:
    def __init__(self, server_hostname: str, http_path: str, access_token: str):
        from databricks import sql
        self.connection = sql.connect(
            server_hostname=server_hostname,
            http_path=http_path,
            access_token=access_token
        )

    def execute_query(self, query: str) -> pd.DataFrame:
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=columns)
        cursor.close()
        return df
