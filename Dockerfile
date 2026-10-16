# RadioNLP Clinical Extraction Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for EasyOCR and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU first to avoid heavy CUDA wheels
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy repository files
COPY . .

# Cloud container port
ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]
