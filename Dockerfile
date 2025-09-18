# Lightweight image for the Streamlit dashboard
FROM python:3.11-slim

# Avoid interactive tzdata etc.
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional, minimal)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy and install
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy project
COPY . /app

EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "dashboard/streamlit_app.py", "--server.address=0.0.0.0"]
