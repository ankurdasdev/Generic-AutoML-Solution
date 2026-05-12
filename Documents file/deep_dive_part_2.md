# Deep-Dive Part 2: Enterprise Scaling Issues

To achieve a truly generic, high-scale solution, we must address these three "silent killers" of production ML systems:

## 1. The "Schema Drift" Bug (ML Pipelines)
- **Problem**: We are currently saving raw models. If the training data has categories (e.g., Rep Names: "Alice", "Bob") and production data has a new category ("Charlie"), the one-hot encoding will mismatch, and the model will crash.
- **Fix**: Wrap the model and its preprocessors (Scaler, Encoder) into a **Scikit-Learn Pipeline**. We save the entire pipeline as a single artifact. The pipeline handles "unknown categories" gracefully.

## 2. The "RAM Exhaustion" Bug (Lazy Loading)
- **Problem**: Our MCP registry loads all trained models into memory at startup. As we scale to hundreds of challenges, the server will crash from memory exhaustion.
- **Fix**: Implement **Lazy Loading**. The `ToolRegistry` will only load a `.joblib` file when that specific tool is called for inference. We will also implement a basic **TTL (Time To Live)** cache to unload models that haven't been used recently.

## 3. The "Token Limit" Bug (Two-Stage Metadata)
- **Problem**: Enterprise Salesforce schemas are massive. Sending a 10MB JSON schema to an LLM will fail or be extremely expensive.
- **Fix**: Implement **Two-Stage Agentic Analysis**:
    - **Discovery**: Send only table names and high-level descriptions.
    - **Drill-Down**: The LLM requests detailed column metadata only for the tables it deems relevant to the challenge.

## 4. Security & Governance
- **Problem**: Lack of authentication on backend endpoints.
- **Fix**: Add a required `X-API-Key` header for all backend requests to prevent unauthorized model training or data access.

---

## Next Steps: Implementation
I am applying these fixes now to ensure the system is ready for the "Opportunity Likelihood" use case, which typically involves complex categorical data and large schemas.
