# Stage 1: The Build Stage
# This stage is used to install all dependencies,
# creating a lean virtual environment that we can copy later.
FROM python:3.11-slim as builder

# Set the working directory for the build stage
WORKDIR /app

# Copy only the requirements file first to leverage Docker's caching
COPY ./requirements.txt .

# Install dependencies into a virtual environment.
# This is a more memory-efficient and clean way to manage packages.
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: The Final Production Stage
# This stage is for the final, lightweight image that will be deployed.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the PATH to include the virtual environment's binaries
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code into the final image
COPY ./app /code/app

# The command to run the application on container start.
# This command correctly uses the $PORT environment variable
# provided by Render and falls back to 10000 if it's not set.
# AFTER
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}