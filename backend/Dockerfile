# ── Stage 1: Build dependencies ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools only in this stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime image ───────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Non-root user for security
RUN groupadd -r fairguard && useradd -r -g fairguard fairguard

WORKDIR /app

# Copy only installed packages from builder (no build tools in final image)
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=fairguard:fairguard . .

# Create writable data directory for SQLite and set ownership
RUN mkdir -p /app/data && chown -R fairguard:fairguard /app/data

# Tell the app where to store SQLite (non-root writable path)
ENV FAIRGUARD_DATA_DIR=/app/data
ENV DATABASE_URL=sqlite:////app/data/fairguard.db

USER fairguard

# Health check using Python (no curl required in slim image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

# Cloud Run injects $PORT — use shell form so the variable is expanded
CMD uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --proxy-headers \
    --forwarded-allow-ips "*"
