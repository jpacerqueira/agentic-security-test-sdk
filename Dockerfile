FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
  && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
  && apt-get purge -y curl && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md /app/
COPY agentic_security /app/agentic_security
COPY examples /app/examples
RUN pip install --no-cache-dir ".[llm]"
ENV RUNS_DIR=/app/runs SKIP_LLM=true
EXPOSE 8090
CMD ["uvicorn", "agentic_security.web.app:app", "--host", "0.0.0.0", "--port", "8090"]
