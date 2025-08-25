# Use a slim Python image
FROM python:3.10-slim

# Install system dependencies (needed for OpenCV & InsightFace)
RUN apt-get update && apt-get install -y \
    build-essential cmake libgl1 libglib2.0-0 git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Flask listens on port 5000
EXPOSE 5000

# Start your app
CMD ["python", "app7.py"]

