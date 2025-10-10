FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# This is the equivalent of Procfile: "python main.py"
ENTRYPOINT ["python", "-m", "cron.cron"]
