# Implementation Plan: AI Deal Strategist Prototype

The goal of this implementation plan is to define a step-by-step, actionable guide for building a functional **prototype** of the AI Deal Strategist. This prototype will validate the end-to-end data flow: from Salesforce data to Databricks ML, exposed via an MCP Server, and consumed by an LLM in a Salesforce LWC.

## User Review Required
> [!IMPORTANT]
> **Prototype Scope Constraint:** To ensure rapid prototyping, we will substitute complex, enterprise-grade integration tools (like Fivetran and Unity Catalog row-level security) with simpler, equivalent approaches (like CSV exports/Python scripts for data ingestion) during this initial phase. Do you approve of this scoping for the prototype?

## Open Questions
> [!WARNING]
> 1. **LLM Orchestration:** Native Salesforce Apex cannot easily run an MCP Client to talk to an MCP Server. The standard approach is to have a Middleware service (e.g., a Python FastAPI app or LangChain/LlamaIndex orchestrator) that receives the chat from Salesforce, acts as the MCP Client to query Databricks, talks to the LLM, and sends the final string back to Salesforce. Should we include this Orchestrator service in the prototype?
> 2. **Salesforce Dev Org:** Do we have a Salesforce Developer Sandbox available with sample Opportunity data to install the LWC?

---

## Proposed Changes

We will execute this prototype in three distinct phases matching the architecture document.

### Phase 1: The Predictive Engine (Backend Prototype)
The goal is to get data into Databricks and generate a model with SHAP values.

1. **Environment Setup:**
   - Provision an Azure Databricks workspace and a connected ADLS Gen2 storage account (or use DBFS for the immediate prototype).
2. **Data Ingestion (Mocked for Prototype):**
   - Export a sample dataset of Opportunities, Accounts, and Activities from Salesforce (via standard Reports or Data Loader) as CSVs.
   - Upload these CSVs to the Databricks workspace (Bronze Layer).
3. **Feature Engineering:**
   - Write a short PySpark notebook to clean the data, handle nulls, and create 2-3 engineered features (e.g., `days_in_stage`, `has_executive_sponsor`).
   - Save the output as a Delta Table (Gold Layer).
4. **Model Training (Databricks AutoML):**
   - Run a Databricks AutoML Classification experiment on the Gold Delta Table, targeting the `IsWon` column.
   - Extract the best model and verify that SHAP values (Feature Importances) are calculated and logged in MLflow.
   - Materialize the SHAP values and Opportunity Scores into a dedicated serving table for fast queries.

---

### Phase 2: The Agentic Layer (MCP Server Prototype)
The goal is to expose the Databricks ML insights to an LLM via the Model Context Protocol.

1. **Project Initialization:**
   - Create a Python project (`sales-intelligence-mcp`) using the official MCP Python SDK (e.g., `fastmcp`).
2. **Databricks Integration:**
   - Integrate the `databricks-sql-connector` to allow the python app to execute SQL queries against the Databricks SQL Warehouse/Cluster.
3. **Tool Implementation:**
   - Define and implement the required tools:
     - `get_opportunity_score(opportunity_id)`: Queries the Gold table for the win probability.
     - `get_risk_factors(opportunity_id)`: Queries the materialized SHAP values for the top negative feature weights for the specific deal.
     - `get_historical_similar_deals(industry, size)`: Queries historical closed-won deals matching the criteria.
4. **Server Deployment (Local/Dev):**
   - Run the MCP server over standard input/output (stdio) or Server-Sent Events (SSE) for local testing.

---

### Phase 3: The User Interface & Execution Flow (Frontend Prototype)
The goal is to close the loop so a user can chat within Salesforce.

1. **LLM Orchestrator Service (Middleware):**
   - Build a lightweight Python FastAPI service that acts as the "Chatbot Backend".
   - This service will:
     - Receive a prompt and Opportunity ID from Salesforce.
     - Instantiate an LLM client (e.g., Anthropic Claude 3.5 Sonnet).
     - Attach the Databricks MCP Server to the LLM.
     - Send the prompt to the LLM, let it use the tools, and return the final synthesized string.
2. **Salesforce Integration (LWC):**
   - Create a basic Lightning Web Component (`aiDealStrategistLWC`) in Salesforce.
   - Design a simple chat UI.
   - Write an Apex Controller to make an HTTP callout to the Orchestrator Service.
   - Embed the LWC on the Opportunity Record Page layout.

---

## Verification Plan

### Automated / Backend Verification
- **Data Validation:** Query the Gold Delta table in Databricks to ensure scores and SHAP values are present.
- **MCP Tool Testing:** Use the MCP Inspector CLI (`npx @modelcontextprotocol/inspector`) to manually invoke `get_risk_factors` and verify it returns valid JSON from Databricks.

### Manual / End-to-End Verification
- **Salesforce Testing:** Open an Opportunity record in Salesforce, type "Why is this deal stuck?" into the LWC.
- Verify that the network logs show the request hitting the Orchestrator.
- Verify that the Orchestrator invokes the MCP tool and queries Databricks.
- Verify that the LLM successfully synthesizes the SHAP values into human-readable strategic advice and displays it in the LWC.
