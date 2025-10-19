FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        && apt-get clean && \
        rm -rf /var/lib/apt/lists/*

# Create directories for uploads, outputs and streamlit config
RUN mkdir -p uploads outputs .streamlit && \
    chmod 777 uploads outputs .streamlit

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (uploads and outputs are protected by .dockerignore)
COPY . .

# Guarantee that the directories are not overwritten and have correct permissions
RUN touch uploads/.keep outputs/.keep .streamlit/.keep && \
    chmod -R 777 uploads outputs .streamlit

# Expose Streamlit port
EXPOSE 8506

# Configure Streamlit
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_PORT=8506 \
    STREAMLIT_SERVER_HEADLESS=true

# Volume declaration to ensure data persistence
VOLUME ["/app/uploads", "/app/outputs", "/app/.streamlit"]

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8506", "--server.address=0.0.0.0"]