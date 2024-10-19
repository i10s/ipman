# Dockerfile for building the service with Poetry
# Dockerfile for production
# File: /docker/Dockerfile

# Use the official Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Create logs directory
RUN mkdir logs

# Install Poetry globally
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files
COPY ../pyproject.toml ../poetry.lock ./

# Install dependencies with Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Copy the rest of the application code
COPY ../src/ .

# Set environment variables for production
ENV FLASK_ENV=production

# Expose port 5000 for the GraphQL API
EXPOSE 5000

# Run the app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
