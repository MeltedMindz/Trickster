# Multi-stage build for AI Religion Architects
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt requirements-backend.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-backend.txt

# Copy application code
COPY ai_religion_architects ./ai_religion_architects
COPY backend ./backend

# Create necessary directories
RUN mkdir -p logs data

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/religion_memory.db
ENV LOG_DIR=/app/logs

# Create volumes for persistent data
VOLUME ["/app/data", "/app/logs"]

# Expose WebSocket port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Start script
COPY scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]