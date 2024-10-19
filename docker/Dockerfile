# Dockerfile for building the service
# File: /docker/Dockerfile

# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY ../requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ../src/ .

# Expose port 5000 for the GraphQL API
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
