FROM python:3.11-slim

WORKDIR /app

# Copy requirements from root
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy config and speed layer code
COPY config/ /app/config/
COPY speed-layer/ /app/speed-layer/

# This Dockerfile is used for both producer and consumer
# The command is specified in docker-compose.yml