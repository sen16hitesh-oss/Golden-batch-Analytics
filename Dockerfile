FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8501

ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV API_URL=http://127.0.0.1:8000

RUN echo '#!/bin/bash\n\
echo "Starting Resilient FastAPI Ingestion Engine on port 8000..."\n\
uvicorn backend.app:app --host 127.0.0.1 --port 8000 &\n\
echo "Starting Analytical Streamlit Control Tower on port 8501..."\n\
streamlit run frontend/dashboard.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
