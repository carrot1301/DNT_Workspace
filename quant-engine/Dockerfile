# Start with a minimal Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY dnt_quant_lab/backend/requirements.txt .

# Install dependencies without caching to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy both backend and frontend directories from the sub-project
COPY dnt_quant_lab/backend ./backend
COPY dnt_quant_lab/frontend ./frontend

# Change working directory to backend where main.py lives
WORKDIR /app/backend

# Inform Docker that the container listens on port 8000
EXPOSE 8000

# Run Uvicorn. $PORT is set by Koyeb automatically
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
