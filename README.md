# QA Automation Portfolio

[![Backend CI](https://github.com/7Lainero7/qa_portfolio/actions/workflows/backend.yml/badge.svg)](https://github.com/7Lainero7/qa_portfolio/actions/workflows/backend.yml)

Пет-проект по автоматизации тестирования для портфолио AQA-инженера.

## Цель

Продемонстрировать навыки автоматизации тестирования на реальных примерах:

- API-тестирование (Python + pytest)
- UI E2E-тестирование (Playwright + TypeScript)
- Data QA (проверка качества данных, миграций, целостности)
- CI/CD (GitHub Actions + GitLab CI)

## Структура проекта

```
qa-portfolio/
├── backend/          # Кит 1: API (FastAPI + pytest)
│   ├── app/          # Сервис
│   ├── tests/        # API-тесты
│   └── requirements.txt
├── frontend/         # Простой UI (Vite + React + TypeScript)
├── e2e/              # Кит 2: UI E2E (Playwright + TypeScript)
│   ├── pages/        # Page Object'ы
│   ├── tests/        # Спеки
│   └── playwright.config.ts
├── data/             # Кит 3: Data QA (PostgreSQL + Faker)
│   ├── schema.sql    # Схема БД
│   ├── generator.py  # Генератор данных
│   └── tests/        # Тесты качества данных
├── docs/             # Документация (тест-кейсы, баг-репорты)
├── .github/          # GitHub Actions workflows
└── .gitlab-ci.yml    # GitLab CI (зеркало для E-soft)
```

## Технологический стек

### Backend
- Python 3.12 + FastAPI
- pytest + httpx (API-тесты)
- SQLAlchemy + PostgreSQL
- pydantic-settings (конфигурация)

### CI/CD
- GitHub Actions (основной CI)
- GitLab CI (зеркало)

### В планах
- Playwright + TypeScript (UI E2E)
- Docker Compose (инфраструктура)
- Faker (генерация данных)

## Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/7Lainero7/qa_portfolio.git
cd qa_portfolio
```

### 2. Настрой PostgreSQL

Убедись, что PostgreSQL запущен локально.

Создай файл `backend/.env` из `backend/.env.example`:

```bash
cp backend/.env.example backend/.env
```

Отредактируй `backend/.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=qa_portfolio
POSTGRES_USER=postgres
POSTGRES_PASSWORD=qwer

API_KEY=test-key
```

### 3. Установи зависимости

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 4. Запусти сервис

```bash
uvicorn app.main:app --reload
```

Сервис будет доступен на http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

### 5. Запусти тесты

Тесты используют отдельную базу `qa_portfolio_test`, которая создаётся автоматически.

```bash
pytest
```

Или с фильтрами:

```bash
pytest -m smoke      # Только smoke-тесты
pytest -m negative   # Только негативные сценарии
pytest -m boundary   # Только граничные значения
```

## API Endpoints

### Health Check
```
GET /health
```
Проверка доступности сервиса (без авторизации).

### Expenses (требует `X-API-Key: test-key`)
```
POST   /api/expenses          # Создать расход
GET    /api/expenses          # Получить список
GET    /api/expenses/{id}     # Получить по ID
PATCH  /api/expenses/{id}     # Обновить
DELETE /api/expenses/{id}     # Удалить
```

## Тестовое покрытие

- Smoke-тесты — критические сценарии
- Negative-тесты — ошибки авторизации (401), отсутствующие ресурсы (404), невалидные данные (422)
- Boundary-тесты — граничные значения через `parametrize`
- Изоляция — каждый тест работает с чистой базой

## Планы развития

- [ ] Frontend (Vite + React + TypeScript)
- [ ] Playwright E2E-тесты
- [ ] Data QA (проверка качества данных)
- [ ] GitLab CI workflow
- [ ] Docker Compose для инфраструктуры
- [ ] Документация (тест-кейсы, баг-репорты)

## Лицензия

MIT