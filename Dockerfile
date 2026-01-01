FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Essentia
RUN apt-get update && apt-get install -y \
    build-essential \
    libyaml-dev \
    libfftw3-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswresample-dev \
    libsamplerate0-dev \
    libtag1-dev \
    libchromaprint-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY essentia/ ./essentia/
COPY src/ ./src/

# Run the service
CMD ["python", "-u", "src/main.py"]
