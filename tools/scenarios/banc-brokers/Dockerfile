# Client de mesure exécuté DANS le réseau Docker (évite le proxy de ports de Docker Desktop)
FROM python:3.12-slim
WORKDIR /demo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bus/ bus/
COPY bench.py ./
ENV RABBITMQ_HOST=rabbitmq KAFKA_BOOTSTRAP=kafka:29092 PYTHONUNBUFFERED=1
ENTRYPOINT ["python"]
