# RadioNLP Clinical Extraction Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for EasyOCR, PDF rendering, and OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install PyTorch CPU with extra-index-url (preserves PyPI)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy repository files
COPY . .

# Cloud container port
ENV PORT=10000
EXPOSE 10000

CMD ["python", "app.py"]
