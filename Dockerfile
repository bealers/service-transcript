FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY transcript_service.py .

EXPOSE 5000
CMD ["python", "transcript_service.py"]
