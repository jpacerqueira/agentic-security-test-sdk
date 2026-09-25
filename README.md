# Agentic Security Test SDK

Two separate deployments of the same security-assessment product. Each subfolder has its own `docker-compose.yml` and its own LiteLLM `llm-gateway`. Deploy one or the other. They are not meant to run together: both publish the app on **8090** and the gateway on **4000**.

```bash
# Google ADK app + this folder's gateway (default ollama / gemma4:latest)
cd google-cloud-showcase
docker compose up --build
# http://localhost:8090   login demo / demobxyz

# LangGraph app + this folder's gateway (default ollama / gemma4:latest)
cd langgraph-showcase
docker compose up --build
# http://localhost:8090   login demo / demobxyz
```

Stop one stack before starting the other (`docker compose down` in that folder). Deterministic mode is the default and does not call a model. LLM mode uses only the gateway in the compose file you started.

## Framework comparison

| Role | `google-cloud-showcase` | `langgraph-showcase` |
|---|---|---|
| Agent framework | Google ADK | LangGraph `StateGraph` |
| LLM client | ADK `LiteLlm` | LangChain `ChatOpenAI` |
| Model gateway | Its own LiteLLM Proxy | Its own LiteLLM Proxy |
| Default profile | `ollama` | `ollama` |
| Default model | `gemma4:latest` | `gemma4:latest` |
| Wire protocol | OpenAI `/v1` | OpenAI `/v1` |
| Model id the app sends | `openai/gemma4:latest` | `gemma4:latest` |
| Google Cloud backend | `LLM_PROFILE=vertex` | `LLM_PROFILE=vertex` |
| AWS backend | `LLM_PROFILE=bedrock` | `LLM_PROFILE=bedrock` |
| Other dormant profile | LM Studio | LM Studio |
| Orchestration | Async generator over phase functions | LangGraph nodes and conditional edges |
| Human gates | `SecurityOrchestrator.wait_gate` | Same gate API, called from graph nodes |
| Web | FastAPI, HTMX, SSE | FastAPI, HTMX, SSE |
| Scanners and reports | Trivy, heuristic AppSec, WeasyPrint PDF | Same scanners and reports |
| Compose project | `google-cloud-showcase/docker-compose.yml` | `langgraph-showcase/docker-compose.yml` |
| Tests | `docker compose run --no-deps --rm agentic-security pytest` in that folder | Same command in that folder |

Switching cloud only changes `LLM_PROFILE` in that folder’s `.env` and restarts that folder’s `llm-gateway`. The app keeps talking to `http://llm-gateway:4000/v1` on its own compose network.
