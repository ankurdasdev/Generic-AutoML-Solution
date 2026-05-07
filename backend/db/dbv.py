import sqlite3
import os

DB_PATH = "backend/db/automl_platform.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Version 1: Challenges and Models
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schema_versions (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("SELECT MAX(version) FROM schema_versions")
    current_version = cursor.fetchone()[0] or 0
    
    if current_version < 1:
        print("Applying migration v1...")
        cursor.execute("""
        CREATE TABLE challenges (
            id TEXT PRIMARY KEY,
            problem_statement TEXT,
            problem_type TEXT,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE trained_models (
            challenge_id TEXT PRIMARY KEY,
            model_path TEXT,
            feature_cols TEXT,
            mlflow_run_id TEXT,
            FOREIGN KEY (challenge_id) REFERENCES challenges(id)
        )
        """)
        cursor.execute("INSERT INTO schema_versions (version) VALUES (1)")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
