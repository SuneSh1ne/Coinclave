# Coinclave

Веб-приложение для систематизации нумизматических коллекций. Позволяет добавлять монеты с фотографиями, фильтровать коллекцию, экспортировать данные и обмениваться монетами с другими коллекционерами.

## Технологии

### Бэкенд
- Python 3.14
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Alembic (миграции)
- JWT (аутентификация)

### Фронтенд
- Vue 3 (Composition API)
- Pinia (управление состоянием)
- Vue Router
- Axios
- Vite

## Функционал

- Регистрация и авторизация (JWT)
- Управление коллекцией монет (CRUD)
- Загрузка изображений (до 4 на монету)
- Фильтрация по стране, металлу, году, состоянию
- Экспорт коллекции в JSON/CSV
- Просмотр коллекций других пользователей
- Обмен монетами (групповые предложения)
- Уведомления о статусе обмена
- Тёмная тема
- Адаптивный дизайн

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/coinclave.git
cd coinclave
```

### 2. Запуск PostgreSQL через Docker

```bash
cd backend
docker-compose up -d
```

### 3. Настройка окружения бэкенда
Создай файл .env в папке backend:

```bash
DATABASE_URL=postgresql+asyncpg://coinclave:coinclave123@localhost:5432/coinclave
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=5
```

### 4. Установка зависимостей бэкенда

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 5. Миграции базы данных

```bash
alembic upgrade head
```

### 6. Запуск бэкенда

```bash
uvicorn app.main:app --reload
```

Сервер будет доступен: http://localhost:8000
Swagger документация: http://localhost:8000/docs

### 7. Установка зависимостей фронтенда

```bash
cd frontend
npm install
```

### 8. Запуск фронтенда

```bash
npm run dev
```

Приложение будет доступно: http://localhost:5173

## API Эндпоинты

### Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/auth/register` | Регистрация пользователя |
| POST | `/auth/login` | Вход в систему |
| GET | `/auth/me` | Информация о текущем пользователе |
| PUT | `/auth/me` | Обновление профиля |

### Коллекция монет

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/coins` | Список монет с фильтрацией |
| POST | `/api/coins` | Добавление монеты |
| GET | `/api/coins/{id}` | Детали монеты |
| PUT | `/api/coins/{id}` | Редактирование монеты |
| DELETE | `/api/coins/{id}` | Удаление монеты |
| GET | `/api/coins/export/{format}` | Экспорт (json/csv) |
| GET | `/api/coins/stats/total-value` | Общая стоимость коллекции |
| GET | `/api/coins/filters/countries` | Список стран пользователя |

### Изображения

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/coins/{id}/images` | Добавить изображение |
| DELETE | `/api/coins/images/{id}` | Удалить изображение |

### Публичные страницы

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/public/feed` | Лента монет (главная страница) |
| GET | `/public/filters/countries` | Список всех стран из всех монет |
| GET | `/public/stats` | Статистика сайта |

### Пользователи

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/users/search` | Поиск пользователей |
| GET | `/users/{id}/collection` | Коллекция другого пользователя |
| GET | `/users/{id}/stats` | Статистика пользователя |

### Обмен монетами

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/exchange/listings` | Монеты, доступные для обмена |
| POST | `/exchange/listings` | Выставить монету на обмен |
| DELETE | `/exchange/listings/{id}` | Снять монету с обмена |
| POST | `/exchange/offers/batch` | Создать групповое предложение обмена |
| GET | `/exchange/offers/sent` | Отправленные предложения |
| GET | `/exchange/offers/received` | Входящие предложения |
| PUT | `/exchange/offers/{id}/accept` | Принять предложение |
| PUT | `/exchange/offers/{id}/reject` | Отклонить предложение |
| PUT | `/exchange/offers/{id}/cancel` | Отменить предложение |

### Уведомления

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/notifications` | Список уведомлений |
| GET | `/notifications/unread-count` | Количество непрочитанных |
| PUT | `/notifications/{id}/read` | Отметить как прочитанное |

### Остановка проекта

```bash
# Остановка PostgreSQL
cd backend
docker-compose down

# Остановка бэкенда и фронтенда — Ctrl+C
```