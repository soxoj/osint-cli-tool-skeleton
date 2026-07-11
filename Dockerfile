# Microservice image: runs the FastAPI HTTP server.
# Build:  docker build -t osint-tool .
# Run:    docker run -p 8080:8080 osint-tool
#         -> OpenAPI docs at http://localhost:8080/docs
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY . .
# Install the package plus the HTTP server extra. Add ',mcp' for MCP support.
RUN pip install --no-cache-dir '.[server]'

EXPOSE 8080

# Override the plugin / proxy / etc. via OSINT_* env vars or a mounted osint.toml.
ENV OSINT_PLUGIN=http_title

ENTRYPOINT ["osint_cli_tool_skeleton"]
CMD ["--server", "0.0.0.0:8080"]
