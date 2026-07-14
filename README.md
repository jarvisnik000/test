# Разработка и настройка CI/CD-пайплайна для веб-приложения управления заметками с тегами

## Описание

Веб-приложение для создания и управления заметками. Пользователь может создавать, просматривать, редактировать и удалять заметки, а также назначать им теги для удобной категоризации и поиска.

### Эндпоинты REST API

| Метод   | Эндпоинт                | Описание                     |
|---------|------------------------|------------------------------|
| GET     | `/api/health`          | Проверка работоспособности   |111
| GET     | `/api/notes`           | Получить все заметки         |
| GET     | `/api/notes/<id>`      | Получить заметку по ID       |
| POST    | `/api/notes`           | Создать новую заметку        |1
| PUT     | `/api/notes/<id>`      | Обновить заметку             |
| DELETE  | `/api/notes/<id>`      | Удалить заметку              |
| GET     | `/api/notes/tag/<tag>` | Поиск заметок по тегу        |

## Технологии

| Технология       | Назначение                             |
|------------------|----------------------------------------|
| Python           | Язык программирования backend          |
| Flask            | Веб-фреймворк                          |
| SQLite           | База данных                            |
| Flake8           | Линтер Python                          |
| Pytest           | Тестирование Python                    |
| Node.js          | Среда выполнения JavaScript            |
| React            | UI библиотека                          |
| Tailwind CSS     | CSS фреймворк                          |
| ESLint           | Линтер JavaScript                      |
| Axios            | HTTP клиент                            |
| Docker           | Контейнеризация                        |
| Docker Compose   | Оркестрация контейнеров                |
| GitHub Actions   | CI/CD автоматизация                    |

## Запуск локально

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python app.py
```

Сервер будет доступен на `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

Приложение будет доступно на `http://localhost:3000`.

## Запуск в Docker

```bash
git clone <URL вашего репозитория>
cd 1
docker-compose up --build
```

После сборки:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5000/api/health`

## CI/CD

### CI Pipeline

Файл: `.github/workflows/ci.yml`

Запускается при **push** и **Pull Request** в ветки `main` и `develop`.

**Этапы CI:**
1. **Backend - Lint & Test** — flake8, pytest с покрытием, проверка импорта Flask
2. **Frontend - Lint & Test** — ESLint, сборка, тесты
3. **Docker Build** — сборка Docker-образов backend и frontend
4. **Integration Validation** — проверка структуры проекта

### CD Pipeline

Файл: `.github/workflows/cd.yml`

Запускается при **merge в ветку `main`** или вручную через `workflow_dispatch`.

**Этапы CD:**
1. Сборка Docker-образов с тегом коммита
2. Локальное тестирование деплоя (запуск контейнеров, healthcheck)
3. Генерация отчета о деплое (`deployment-report.md`)
4. Сохранение отчета как артефакта (доступен 30 дней)

## Переменные окружения

### Backend (`.env`)

| Переменная      | Описание                    | Значение по умолчанию    |
|-----------------|-----------------------------|--------------------------|
| `FLASK_ENV`     | Режим запуска Flask         | `development`            |
| `PORT`          | Порт сервера                | `5000`                   |
| `DATABASE_URL`  | Путь к базе данных SQLite   | `sqlite:///notes.db`     |

### Frontend (встроены в `docker-compose.yml`)

| Переменная           | Описание                          | Значение по умолчанию           |
|----------------------|-----------------------------------|---------------------------------|
| `REACT_APP_API_URL`  | Базовый URL для API-запросов      | `http://localhost:5000/api`     |

## Структура проекта

```
1/
├── backend/                  # Python Flask API
│   ├── app.py                # Основное приложение Flask (REST endpoints)
│   ├── database.py           # SQLite инициализация и подключение
│   ├── models.py             # Модель Note (CRUD операции)
│   ├── Dockerfile            # Docker-образ для backend
│   ├── requirements.txt      # Python зависимости
│   ├── .env.example          # Шаблон переменных окружения
│   └── tests/
│       └── test_api.py       # Unit-тесты API (pytest)
├── frontend/                 # React приложение
│   ├── src/
│   │   ├── App.jsx           # Главный компонент
│   │   ├── api.js            # Axios клиент для API
│   │   ├── styles.css        # Tailwind CSS стили
│   │   ├── index.js          # Точка входа React
│   │   └── components/
│   │       ├── NoteForm.jsx  # Форма создания/редактирования
│   │       ├── NoteItem.jsx  # Карточка заметки
│   │       ├── NoteList.jsx  # Список заметок
│   │       └── TagFilter.jsx # Фильтр по тегам
│   ├── Dockerfile            # Multi-stage сборка (node → nginx)
│   ├── nginx.conf            # Nginx конфигурация (прокси API)
│   └── package.json          # Node.js зависимости
├── .github/workflows/
│   ├── ci.yml                # CI pipeline (lint, test, docker build)
│   └── cd.yml                # CD pipeline (deploy, отчет)
├── docker-compose.yml        # Оркестрация контейнеров
├── .eslintrc.js              # ESLint конфигурация
├── .gitignore                # Игнорируемые файлы
└── README.md                 # Документация проекта
```
