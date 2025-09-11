# Stage 1: The Builder Stage
FROM python:3.11-slim as builder

WORKDIR /code

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file
COPY ./requirements.txt .

# --- DEBUGGING STEP ---
# This line prints the content of the requirements.txt file to the build log
# so we can see which version Render is using.
RUN cat /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --only-binary :all: -r requirements.txt

# ---
# Stage 2: The Final Production Stage
FROM python:3.11-slim

WORKDIR /code

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY ./app ./app

# Set the PATH to use the virtual environment's executables
ENV PATH="/opt/venv/bin:$PATH"

# Add a non-root user for better security
RUN useradd --create-home appuser
USER appuser

# Command to run the application using the FULL PATH to uvicorn
CMD ["sh", "-c", "/opt/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]