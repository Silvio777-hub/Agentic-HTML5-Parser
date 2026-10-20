# ==============================================================================
# Dockerfile — Agentic AI HTML5 Parser Container
# Multi-stage lightweight environment for running the parser, test suites,
# comparative benchmarks, and live quality dashboard.
# ==============================================================================

# 1. Base Image: Use official lightweight Python 3.11 Slim
FROM python:3.11-slim AS base

# 2. Environment Variables:
# - PYTHONUNBUFFERED=1 ensures real-time stdout logs without buffering
# - PYTHONDONTWRITEBYTECODE=1 prevents creation of .pyc files inside container
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# 3. Set Container Working Directory
WORKDIR /app

# 4. Install system build dependencies (git for upstream tests, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy & Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir matplotlib python-docx

# 6. Copy Application Source Code, Scripts, and Dashboards
COPY . .

# 7. Expose Web Dashboard Port
EXPOSE 8080

# 8. Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/dashboard/ || exit 1

# 9. Default Command: Start the live dashboard & parser API server
CMD ["python", "scripts/serve_dashboard.py", "--no-browser", "--port", "8080"]
