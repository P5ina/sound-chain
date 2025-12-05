FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for audio and GPIO
RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    libsndfile1 \
    # Build dependencies for lgpio
    swig \
    python3-dev \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

# Expose WebSocket port
EXPOSE 8765

# Run the server
CMD ["python", "-u", "main.py"]
