FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies for audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

# Expose WebSocket port
EXPOSE 8765

# Note: GPIO/buzzer will be simulated in Docker
# For real buzzer, run natively on Raspberry Pi with system lgpio

# Run the server
CMD ["python", "-u", "main.py"]
