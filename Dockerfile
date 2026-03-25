# Use a matching Python version
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-hin \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Setup non-root user for Hugging Face Spaces (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy and install requirements
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Pre-download models to cache into the image
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')"

# Copy application code
COPY --chown=user . .

# Expose the default Gradio/HF port
EXPOSE 7860

# Launch application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
