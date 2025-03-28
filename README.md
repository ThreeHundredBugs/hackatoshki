# Сервис автоматизации фикса алертов OpsGenie

Это внутренний тул для команд которые используют OpsGenie для дежурств. Особенно актуально для DevOps.
В OpsGenie часто прилетают однообразные алерты, которые можно автоматизировать.
Мы хотим предоставить возможность добавлять кастомные обработчики для легких фиксов и вызывать их из OpsGenie.
В OpsGenie настроена интеграция, которая отправляет события о запуске кастомных экшенов по вебхуку, а мы их получаем и обрабатываем.
Запуск в опсжени выглядит так:
![image](docs/images/opsgenie_web_interface.png)

Мы нажимаем на кнопку и наш сервис выполняет какую-то логику по фиксу алерта.
По результатам теста обработчик должен отписаться в комменты (notes) алерта.

Примеры проблем, которые должен решать сервис:
- Перезагрузить приложение в Kubernetes (актуально для сентри, airbyte)
- Накинуть места на диске в БД
- Проверить какие сервисы деплоились недавно
- Удалить неудачный стейджинг spa
- Сделать ПР в гитхаб чтобы потюнить ресурсы

![image](docs/images/diagram.png)


Фатальный недостаток заключается в том, что мы не успели сделать даже минимально рабочий проект
¯\_(ツ)_/¯

Ниже AI-generated описание проекта

# Event Processing Service

Service to process Opsgenie events via webhook integration, with easily extendable event handlers.

## Requirements

- Python 3.13+
- Docker and Docker Compose
- pip (for local development)

## Development Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r conf/requirements.txt
```

3. Run the application locally:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

## Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The application will be available at http://localhost:8080

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## Project Structure

```
.
├── conf/           # Configuration files
│   └── requirements.txt
├── src/
│   ├── core/      # Core service components
│   ├── services/  # External service integrations
│   ├── handlers/  # Event handlers
│   ├── models/    # Pydantic models
│   └── utils/     # Utility functions
└── docker/        # Docker-related files
```

## Development Guidelines

1. Follow type hints strictly
2. Use Black for code formatting
3. Use isort for import sorting
4. Use mypy for type checking
5. Use ruff for linting

Run quality checks:
```bash
isort .
mypy .
ruff check .
```
