# QA Automation Portfolio

[![Backend CI](https://github.com/<твой-логин>/qa_portfolio/actions/workflows/backend.yml/badge.svg)](https://github.com/<твой-логин>/qa_portfolio/actions/workflows/backend.yml)
[![E2E CI](https://github.com/<твой-логин>/qa_portfolio/actions/workflows/e2e.yml/badge.svg)](https://github.com/<твой-логин>/qa_portfolio/actions/workflows/e2e.yml)
[![Data QA CI](https://github.com/<твой-логин>/qa_portfolio/actions/workflows/data-qa.yml/badge.svg)](https://github.com/<твой-логин>/qa_portfolio/actions/workflows/data-qa.yml)
Пет-проект по автоматизации тестирования для портфолио AQA-инженера.

## Цель

Продемонстрировать навыки автоматизации тестирования на реальных примерах:

- API-тестирование (Python + pytest)
- UI E2E-тестирование (Playwright + TypeScript)
- Data QA (проверка качества данных, миграций, целостности)
- CI/CD (GitHub Actions)

## Структура проекта

```text
qa_portfolio/
├── backend/          # Кит 1: API (FastAPI + pytest, 90% coverage)
├── frontend/         # Кит 2: UI (Vite + React + TypeScript)
├── e2e/              # Кит 3: E2E (Playwright + POM)
├── data/             # Кит 4: Data QA (Faker, ETL staging→mart, тесты целостности)
├── docs/             # Тест-кейсы, баг-репорты и known issues
├── .github/          # CI/CD workflows (Backend, E2E, Data QA)
└── README.md
```


## Технологический стек

### Backend
- Python 3.12 + FastAPI
- pytest + httpx (API-тесты)
- SQLAlchemy + PostgreSQL
- pydantic-settings (конфигурация)

### Frontend
- Vite + React 18 + TypeScript
- Обработка ошибок API с рендером сообщений в DOM (`data-testid="error-message"`)

### E2E
- Playwright Test (TypeScript)
- Page Object Model + кастомные фикстуры
- Негативные UI-сценарии с перехватом сети (`page.route`)
- Конфигурация через переменные окружения (`e2e/.env.example`)

### CI/CD
- GitHub Actions (основной CI)

## Быстрый старт

### 1. Подготовка окружения
Убедись, что PostgreSQL запущен локально.
```bash
git clone https://github.com/<твой-логин>/qa_portfolio.git
cd qa_portfolio
```

### 2. Backend & API Tests
```bash
cd backend
cp .env.example .env  # Отредактируй POSTGRES_PASSWORD при необходимости
python -m venv .venv && source .venv/bin/activate  # или .venv\Scripts\activate на Windows
pip install -r requirements.txt
pytest  # Запуск тестов с coverage
uvicorn app.main:app --reload  # Запуск сервера на :8000
```


### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env  # Убедись, что VITE_API_URL указывает на http://127.0.0.1:8000
npm run dev  # Запуск на :5173
```


### 4. E2E Tests (Playwright)
*Требует запущенного Backend (шаг 2)*
```bash
cd e2e
npm install
npx playwright install
npx playwright test  # или npm run test:ui для интерактивного режима
```


### 5. Data QA Tests
*Требует запущенного PostgreSQL. Тесты автоматически сгенерируют и мигрируют данные.*
```bash
cd data
# Конфигурация берётся из ENV или backend/.env (POSTGRES_* переменные) —
# отдельный .env в data/ не нужен.
pip install -r requirements.txt
# ВАЖНО: запускай на изолированной базе (например, qa_portfolio_data_test):
# генератор делает DROP TABLE по своей схеме. Если POSTGRES_DB=qa_portfolio,
# тесты будут пропущены с понятным сообщением.
POSTGRES_DB=qa_portfolio_data_test pytest -v -m data_qa
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
- Порог coverage — `--cov-fail-under=90` в `backend/pytest.ini`: CI падает, если покрытие API ниже 90%
- E2E негативные сценарии UI (`e2e/tests/negative.spec.ts`) — клиентская валидация и ошибки API (422/500), отображаемые в DOM

## Known Issues

Открытые проблемы и принятые дизайн-решения задокументированы в [docs/known_issues.md](docs/known_issues.md).

## Тест-кейсы

Примеры формализованных тест-кейсов (API создания расхода) — в [docs/test_cases.md](docs/test_cases.md).

## Планы развития

- [x] Добавление E2E тестов на негативные сценарии UI (обработка ошибок API в DOM)
- [ ] Переход на Alembic для управления миграциями БД
- [ ] Нагрузочное тестирование API (Locust)


## Лицензия

MIT