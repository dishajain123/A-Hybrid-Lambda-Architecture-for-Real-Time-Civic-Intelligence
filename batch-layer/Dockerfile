FROM python:3.11-slim

WORKDIR /app

# Copy requirements from root
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy config and batch layer code
COPY config/ /app/config/
COPY batch-layer/ /app/batch-layer/

CMD ["python", "-u", "batch-layer/flink_job.py"]