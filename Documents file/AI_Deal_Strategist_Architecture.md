# AI Deal Strategist: Architecture Design Document

## 1. Objective
To build an "AI Sales Strategist" that goes beyond static opportunity scoring. The objective is to empower Sales Representatives with an embedded, conversational AI Assistant that can explain win/loss probabilities, strategize on stalled deals, and draw insights from deep historical data using advanced machine learning.

## 2. Problem Statement
Traditional Opportunity Scoring (like Salesforce Einstein or standard ML pipelines) provides a raw "Likelihood to Close" percentage (e.g., 60%). This presents three main problems:
1. **Lack of Actionability:** A static score does not tell a Sales Rep *why* the score is 60% or *what* they can do to improve it.
2. **The "Black Box" Problem:** Built-in CRM AI solutions often lack transparency. Users cannot see the mathematical reasoning, tune the hyperparameters, or own the intellectual property of the model.
3. **Compute and Data Limitations:** Calculating complex, multi-variable features (e.g., historical velocity comparisons across industries over a 10-year span) exceeds the native compute and API limits of standard CRM platforms like Salesforce.

## 3. Proposed Solution
Instead of just pushing a static number to the sales team, we propose an Agentic AI architecture. This system uses a **Data Lake** for highly scalable storage, **Databricks** as the heavy-lifting analytical engine and compute layer, **AutoML** to democratize the machine learning process, and a **Model Context Protocol (MCP) Server** to bridge the gap between an LLM-powered chat assistant and the deep analytical data.

Sales reps will interact with a Custom Lightning Web Component (LWC) inside Salesforce—an embedded chat interface called the **"AI Deal Strategist."**

### Why this Tech Stack?
- **Data Lake (The Storage Foundation):** A centralized, highly scalable repository (like Azure Data Lake or AWS S3) to securely store decades of historical CRM data alongside external data sets at a fraction of the cost.
- **Databricks (The Compute Engine & Brain):** Sits on top of the Data Lake. It provides the distributed compute power to process massive datasets and uses **AutoML** to find the absolute best algorithm to predict win/loss. Crucially, it identifies the Feature Importances (the *why* behind the prediction).
- **The MCP Server (The Bridge):** We build a custom MCP Server that hooks into Databricks. When a Sales Rep asks an LLM (like Claude or a custom Copilot), "Why is the Acme Corp deal stalling and how do I save it?", the LLM uses the MCP server to dynamically query the ML model's reasoning and historical Databricks data.

### Why Extract Salesforce Data to a Data Lake?
A critical question often raised is: *"If the data is already in Salesforce, why move it to a Data Lake?"*
1. **Governor Limits and Compute Constraints:** Salesforce is a transactional system optimized for real-time operations, protected by strict governor limits (CPU timeouts, query row limits). It is impossible to run complex, multi-variable aggregations across 10 years of history (e.g., calculating rep velocity vs. industry average) natively in Salesforce without timing out. Databricks provides the distributed compute necessary for these heavy analytical workloads.
2. **Prohibitive Storage Costs:** Salesforce data storage is notoriously expensive per gigabyte. Storing millions of historical records, activities, and audit trails indefinitely inside Salesforce is cost-prohibitive. A Data Lake offers essentially bottomless storage for pennies on the dollar.
3. **Data Enrichment (Breaking Silos):** The most accurate ML models look beyond CRM data. A Data Lake allows us to blend Salesforce Opportunity data with external datasets (product usage telemetry, ERP billing data, marketing analytics) that do not, and should not, natively live in Salesforce.
4. **Machine Learning Feasibility:** You cannot train advanced, custom machine learning models directly inside the Salesforce database architecture. The data must be extracted to an environment (Data Lake + Databricks) that supports modern ML frameworks and massive parallel processing.

## 4. Existing Solutions in the Industry
* **Salesforce Einstein Opportunity Scoring:** Built-in, easy to use, but acts as a black box. You cannot tweak the algorithm or perform massive custom feature engineering over decades of data.
* **Standard ETL -> ML -> Salesforce Batch Push:** Extracts data to a warehouse, trains a model, and pushes a score back via API. It solves the math problem but still only gives the rep a "dumb number" without real-time, conversational explainability.

---

## 5. Architecture Level Design (In-Depth)

Our architecture is divided into three distinct phases that form a continuous, real-time loop between the CRM, the Data Lake, and the LLM.

### Phase 1: The Predictive Engine (Backend)

We treat Databricks as the analytical factory, completely separate from the operational kitchen of Salesforce.

* **The Extract (Nightly Sync):** We set up a pipeline (e.g., Fivetran or Databricks natively) that pulls a nightly snapshot of the Salesforce Opportunity, Account, and Activity tables into Databricks.
* **The Factory (Databricks + AutoML):** Databricks crunches the historical data, engineers complex features (deal velocity, historical win rates per rep), and uses AutoML to train the model.
* **The Training:** Databricks **AutoML** runs weekly to train a classification model (Win/Loss). It outputs the model AND the SHAP values (the reasons why a prediction was made).
    * *Eliminates the "Data Scientist Bottleneck":* Building this manually requires hiring a specialized, highly-paid Machine Learning Engineer to tune hyperparameters. AutoML democratizes this. We let the compute power do the heavy lifting, allowing your existing data engineers/Salesforce devs to manage the pipeline.
    * *Continuous Learning (Preventing "Model Drift"):* Markets change. Databricks AutoML can be scheduled to automatically retrain the model every month with the latest closed-won/closed-lost data, ensuring the predictive score is always adapting to current market realities without manual intervention.
    * *Total Transparency (The White Box):* Unlike Salesforce Einstein, Databricks AutoML gives us the exact mathematical breakdown (SHAP values) of why it made a prediction. We own the IP, we own the logic, and we can prove it to the sales reps.

### Phase 2: The Agentic Layer (The MCP Magic)

This is where the architecture transitions from standard Machine Learning to Generative AI.

* **The Server:** We write a Python MCP Server (`sales-intelligence-mcp`). It has tools like `get_opportunity_score()`, `get_risk_factors()`, and `get_historical_similar_deals()`.
* **The Core Principle:** Our MCP server **does not connect to Salesforce**. Instead, our MCP server connects directly to Databricks SQL and MLflow. When the LLM asks, "Why is this deal at risk?", the MCP server bypasses Salesforce entirely. It queries the Databricks analytical engine to get the deep, heavy-math insights that Salesforce simply doesn't have the compute power to provide.

### Phase 3: The User Experience & Execution Flow

We will build a **Custom Lightning Web Component (LWC)** directly on the Salesforce Opportunity Record Page. Let's call it the "AI Deal Strategist." It looks like a chat interface embedded right next to the Opportunity details.

#### Step-by-Step Execution Flow:
1. **The Trigger (User Prompt):**
   * *The Rep:* Opens the "TechCorp Enterprise Deal" in Salesforce. The deal has a Databricks-generated win score of 45%.
   * *The Rep types into the LWC:* "Why is this deal stuck at 45% and what exactly should my next step be?"
2. **The Routing (Salesforce -> LLM):**
   * The LWC sends this prompt, along with the Opportunity ID, to our core LLM application (e.g., OpenAI or Anthropic hosted securely).
3. **The Bridge (LLM -> MCP Server):**
   * The LLM realizes it needs real-time, analytical context to answer. It uses a tool call to hit our **MCP Server**.
   * *The Request:* "Execute `get_risk_factors(opportunity_id=123)` and `get_historical_similar_deals(industry='Software', size='Enterprise')`."
4. **The Brain (MCP -> Databricks):**
   * The MCP Server translates these requests into SQL/API calls and queries Databricks directly.
   * Databricks instantly runs the heavy math across 10 years of data and returns the feature importances (e.g., lack of executive sponsor) and historically similar won deals.
5. **The Final Response (LLM -> Sales Rep):**
   * The LLM synthesizes the data returned by the MCP Server.
   * *The Reply in LWC:* "TechCorp is at a 45% win probability. The ML model flagged that there is no 'Executive Sponsor' attached, which historically drops win rates by 30% for deals over $100k. I suggest you multi-thread and contact their VP."