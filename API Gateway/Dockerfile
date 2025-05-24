# syntax=docker/dockerfile:1

# --- Builder stage: install dependencies with Poetry ---
FROM python:3.13-slim AS builder

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Копируем файлы манифестов для установки зависимостей
COPY pyproject.toml poetry.lock* ./

# Настраиваем Poetry и устанавливаем зависимости (исключая dev-группу и без установки пакета проекта)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev --no-root

# --- Runtime stage: минимальный образ для запуска ---
FROM python:3.13-slim AS runtime

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Копируем установленные пакеты и исполнители из образа билдера
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
EXPOSE 8000
# Копируем исходники приложения
COPY . /app
# Открываем порт, на котором работает FastAPI
ENV PYTHONPATH="/app/src"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]