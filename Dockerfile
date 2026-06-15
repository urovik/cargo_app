FROM python:3.14-slim

# Установим базовые утилиты, если понадобятся при отладке (опционально)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости и ставим их ДО копирования кода — чтобы кэш слоёв работал
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Экспонируем порт
EXPOSE 8000

# Важно: слушаем 0.0.0.0, иначе из контейнера не достучаться
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
