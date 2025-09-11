# Stage 1: The Build Stage
FROM python:3.11-slim as builder

# Set the working directory for the build stage
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt .

# Use a non-standard but often more memory-efficient install command
# This avoids the dependency resolution engine which can be memory-heavy
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt

# Stage 2: The Final Production Stage
FROM python:3.11-slim

# Set the working directory
WORKDIR /code

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code
COPY ./app /code/app

# The command to run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}