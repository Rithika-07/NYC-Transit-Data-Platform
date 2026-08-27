FROM python:3.11-slim

WORKDIR /app

COPY main.py .

RUN pip install --no-cache-dir google-cloud-bigquery requests

CMD ["python", "main.py"]