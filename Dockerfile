# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir pip-tools && \
    pip-compile pyproject.toml --output-file=requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy the .env file first
COPY .env .

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5002

# Command to run the application
CMD ["python", "app.py"]
