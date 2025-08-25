# Use Python 3.7
FROM python:3.7-slim

# Set working directory
WORKDIR /app

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port 5000
EXPOSE 5000

# Run Flask
CMD ["python", "app.py"]
