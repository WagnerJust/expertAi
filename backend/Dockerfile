# Use official Python 3.11 slim image
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies if needed (optional, e.g., build-essential, libmagic, etc.)
# RUN apt-get update && apt-get install -y ...

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Ensure venv is used for all future RUN/CMD
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
