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
        Executes queries in batches to support high-scale data extraction.
        Uses XlsxWriter memory optimization for large files.
        """
        file_path = os.path.join(self.output_dir, "training_data_template.xlsx")
        
        # Use a context manager to ensure the writer is closed properly
        with pd.ExcelWriter(file_path, engine='xlsxwriter', engine_kwargs={'options': {'constant_memory': True}}) as writer:
            for challenge_id, query in queries.items():
                # For high-scale, we stream data in chunks from Databricks
                # Here we simulate chunked processing for the template
                chunks = connector.execute_query_stream(query, chunk_size=100000)
                
                start_row = 0
                for i, chunk in enumerate(chunks):
                    # Add Target column only to the first chunk's header
                    if 'Target' not in chunk.columns:
                        chunk['Target'] = ""
                    
                    # Write chunk to sheet
                    chunk.to_excel(writer, sheet_name=challenge_id, index=False, startrow=start_row, header=(i == 0))
                    start_row += len(chunk)

        return file_path

class MockConnector:
    """Mock connector with streaming support"""
    def execute_query(self, query: str) -> pd.DataFrame:
        return pd.DataFrame({"feat": [1], "Target": [""]})

    def execute_query_stream(self, query: str, chunk_size: int = 1000):
        # Simulate streaming two chunks of data
        yield pd.DataFrame({"feature_1": range(chunk_size), "feature_2": [0.5]*chunk_size})
        yield pd.DataFrame({"feature_1": range(chunk_size, chunk_size*2), "feature_2": [0.8]*chunk_size})

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
