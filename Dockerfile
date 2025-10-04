FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-traditional \
    dos2unix \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN dos2unix /app/wait_for_db.sh && chmod +x /app/wait_for_db.sh

# 👇 Запускаем явно через bash
CMD ["bash", "wait_for_db.sh"]
