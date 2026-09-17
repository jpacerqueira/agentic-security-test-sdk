FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 libharfbuzz0b libharfbuzz-subset0 libffi-dev shared-mime-info \
    fonts-liberation fonts-dejavu-core \
  && curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin \
  && apt-get purge -y curl && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md /app/
COPY agentic_security /app/agentic_security
COPY examples /app/examples
COPY tests /app/tests
RUN pip install --no-cache-dir ".[llm,dev]"
ENV RUNS_DIR=/app/runs SKIP_LLM=true PYTHONUNBUFFERED=1 LOG_DIR=/app/logs
EXPOSE 8090
CMD ["uvicorn", "agentic_security.web.app:app", "--host", "0.0.0.0", "--port", "8090", "--log-level", "info"]
