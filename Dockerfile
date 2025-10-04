FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости для psycopg2 и netcat
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-traditional \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Делаем скрипт wait_for_db.sh исполняемым
RUN dos2unix /app/wait_for_db.sh && chmod +x /app/wait_for_db.sh

# По умолчанию запускаем контейнер живым для тестов
CMD ["tail", "-f", "/dev/null"]
