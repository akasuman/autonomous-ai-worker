# Stage 1: The Builder Stage
FROM python:3.11-slim as builder

WORKDIR /code

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
# --- FIX: Removed the --only-binary :all: flag ---
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---
# Stage 2: The Final Production Stage
FROM python:3.11-slim

WORKDIR /code
COPY --from=builder /opt/venv /opt/venv
COPY ./app ./app
ENV PATH="/opt/venv/bin:$PATH"
RUN useradd --create-home appuser
USER appuser
CMD ["sh", "-c", "/opt/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]