# Architecture & Functionality Summary: Generic AutoML Solution

## 1. High-Level Design Philosophy
The solution is built on a **"Micro-Model" Architecture**. Instead of creating one large, monolithic AI model, we dynamically generate small, highly specialized "micro-models" for each business challenge (e.g., "Opportunity Likelihood", "Fan Anomaly"). This ensures maximum accuracy, lower latency, and extreme scalability.

---

## 2. Phase 1: The Training Phase (Step-by-Step)

### [Part 1] Agentic Metadata Analysis
- **Input**: User provides a Problem Statement (e.g., "Improve Sales Velocity") and specific Challenges (C1, C2...).
- **LLM Agent**: A Senior Data Scientist LLM analyzes the organization's **JSON Metadata Schema**.
- **Output**: 
    1. It identifies exactly which columns/tables are required for each challenge.
    2. It classifies the challenge type (Classification vs. Regression).
    3. It generates a **Databricks SQL Query** optimized for your Data Lake to fetch these features.

### [Part 2] Backend Data Preparation
- **Execution**: The backend runs the generated SQL queries via a Databricks connector.
- **Excel Generation**: It produces a single Excel file where each challenge (C1, C2...) has its own tab.
- **Target Injection**: A new column named **'Target'** is appended as the last column, ready for human labeling.

### [Part 3] Human-in-the-Loop Labeling
- **Manual Step**: The user downloads the generated Excel, fills in the 'Target' column (e.g., 0 for Lost, 1 for Won), and uploads it back.
- **UI Tracking**: The platform shows real-time "Thinking Logs" (Plan -> Act -> Observe) so the user understands exactly how the AI mapped the data.

### [Part 4] AutoML Competition Engine
- **Competition Loop**: The system triggers a competition between **20-30 model candidates** (Random Forest, XGBoost, LightGBM, CatBoost, etc.).
- **Evaluation**: Each model is cross-validated and tuned. The "Champion" is selected based on the best F1-score (classification) or R2-score (regression).
- **MLFlow**: The entire experiment history and the champion model are logged and versioned in **MLFlow**.

---

## 3. Phase 2: The Production Phase (Inference)

### Dynamic Tool Registration
- Once a model is trained, it is automatically registered as a **Tool** in the **Model Context Protocol (MCP)** registry.
- This registry is dynamic; the Production Agent can "see" new models immediately without a system restart.

### The Production Chat Interface
- **User Prompt**: A user asks a natural language question (e.g., "Is the Acme deal at risk?").
- **Inference Agent**: An LLM identifies which specific Micro-Model tool is needed to answer the question.
- **Adaptive Data Fetching**: The MCP tool fetches the **last 100-200 records** for that specific entity from the Data Lake.
- **Micro-Model Inference**: The data is passed to the micro-model, which returns a prediction and probability.
- **Synthesis**: The LLM synthesizes the model's raw JSON output into a tailored, business-ready response for the user.

---

## 4. Technical Governance
- **DBV (Database Versioning)**: All platform metadata (challenge mappings, model paths, timestamps) is managed through a version-controlled SQLite database.
- **MLFlow**: Acts as the central registry for model audit trails, ensuring every prediction can be traced back to its specific training run.
- **Premium Frontend**: Built with **React & Vite**, utilizing a modern light theme, framer-motion animations, and Lucide icons for a top-tier user experience.
