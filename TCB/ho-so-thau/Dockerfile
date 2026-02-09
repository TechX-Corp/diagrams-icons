FROM python:3.12-slim

# Install system dependencies for document rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    poppler-utils \
    fonts-liberation \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create non-root user
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

# Copy dependency files first (cache layer)
COPY pyproject.toml ./

# Install Python dependencies
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY scripts/ ./scripts/
COPY templates/ ./templates/

# Switch to non-root user
USER appuser

# Default command: keep container running for rendering requests
CMD ["sleep", "infinity"]
