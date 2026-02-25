# Dockerfile for Lesson Shorts Generator
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files AND README (required by pyproject.toml)
COPY README.md pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync

# Copy application code
COPY src/ ./src/

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8001

# Run the application
CMD ["uv", "run", "uvicorn", "shorts_generator.main:app", "--host", "0.0.0.0", "--port", "8001"]
