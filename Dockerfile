FROM python:3.11-slim

WORKDIR /app

# Install compilation utilities required for database drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Open interface routing windows
EXPOSE 8000
EXPOSE 8501

ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV API_URL=http://127.0.0.1:8000

# Native shell array execution sequence to prevent line-break script mangling
CMD ["sh", "-c", "uvicorn backend.app:app --host 127.0.0.1 --port 8000 & streamlit run frontend/dashboard.py --server.port 8501 --server.address 0.0.0.0"]
