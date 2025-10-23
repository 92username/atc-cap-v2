FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN useradd --create-home --uid 1000 --shell /bin/bash appuser

# cria o diretório de uploads persistentes e ajusta permissões
RUN mkdir -p /data/uploads && chmod -R 777 /data/uploads

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        && apt-get clean && \
        rm -rf /var/lib/apt/lists/*

# Create directories for streamlit config
RUN mkdir -p .streamlit && \
    chmod 777 .streamlit && \
    chown -R appuser:appuser .streamlit

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (uploads and outputs are protected by .dockerignore)
COPY . .
RUN chown -R appuser:appuser /app /data/uploads

# Guarantee that the directories are not overwritten and have correct permissions
RUN touch .streamlit/.keep && \
    chmod -R 777 .streamlit && \
    chown -R appuser:appuser .streamlit

# Expose Streamlit port
EXPOSE 8506

# Configure Streamlit
ENV OUTPUT_DIR=/data/uploads \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_PORT=8506 \
    STREAMLIT_SERVER_HEADLESS=true

# Volume declaration to ensure data persistence
VOLUME ["/data/uploads", "/app/.streamlit"]

# Run Streamlit
USER appuser

CMD ["streamlit", "run", "app.py", "--server.port=8506", "--server.address=0.0.0.0"]