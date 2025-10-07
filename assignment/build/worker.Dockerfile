FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Optional: native Build-Tools
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# dependencies 
COPY pyproject.toml uv.lock ./

# create venv
RUN uv venv .venv

# Erstelle virtuelle Umgebung und installiere Dependencies
RUN uv sync --frozen --no-dev --group worker

# Anwendungscode kopieren
COPY api /app/api

FROM python:3.11-slim AS runtime

WORKDIR /app

# copy venv and app from builder
COPY --from=builder /app/.venv /app/.venv
COPY api /app

# Set environment variables
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
