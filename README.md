# Django Comments

SPA-приложение для создания и обсуждения комментариев с поддержкой вложенных ответов, CAPTCHA, загрузки файлов и обновления в реальном времени.

**Демонстрация:** http://92.5.102.106

## Возможности

- Создание корневых комментариев и ответов неограниченной глубины.
- Сортировка корневых комментариев по имени пользователя, email и дате создания; сортировка по умолчанию — новые сверху (LIFO).
- Пагинация списка комментариев.
- Серверная CAPTCHA перед созданием комментария.
- Проверка имени пользователя: только латинские буквы и цифры.
- Проверка email и необязательной домашней страницы.
- Защита от XSS: пользовательский текст очищается, разрешены только безопасные HTML-теги.
- Загрузка изображений JPG, GIF и PNG с пропорциональным уменьшением до 320×240 px.
- Загрузка текстовых файлов TXT размером до 100 KB.
- Сохранение технических данных запроса: IP-адреса и User-Agent.
- Обновление списка через WebSocket без перезагрузки страницы.

## Технологии

| Уровень | Используемые технологии |
| --- | --- |
| Frontend | React, Vite, CSS |
| Backend API | Django, Django REST Framework |
| Real-time | Django Channels, Daphne, WebSocket |
| Фоновые задачи | Celery, Redis |
| База данных | PostgreSQL |
| Reverse proxy / static | Nginx |
| Контейнеризация | Docker, Docker Compose |


## Запуск для разработки

### Требования

- Docker Desktop и Docker Compose.

### 1. Создать файл окружения

```bash
cp .env.example .env
```

При необходимости измените значения PostgreSQL и Django-настроек в `.env`.

### 2. Собрать и запустить сервисы

```bash
docker compose up --build
```

В отдельном терминале примените миграции:

```bash
docker compose exec backend python manage.py migrate
```

Приложение будет доступно по адресу, указанному в конфигурации frontend. API Django обычно доступно на `http://127.0.0.1:8000`.

## Production-запуск

Для production используется отдельная конфигурация Docker Compose:

```bash
cp .env.production.example .env.production
```

Перед запуском обязательно задайте собственные значения `SECRET_KEY` и `POSTGRES_PASSWORD`, а также укажите допустимые хосты в `ALLOWED_HOSTS`.

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up --build -d
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python manage.py migrate
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python manage.py collectstatic --noinput
```

Проверить состояние сервисов:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```


## API и WebSocket

| Метод | Endpoint | Назначение |
| --- | --- | --- |
| `GET` | `/api/comments/` | Список корневых комментариев, сортировка и пагинация |
| `POST` | `/api/comments/` | Создание комментария или ответа |
| `GET` | `/api/captcha/` | Получение CAPTCHA |
| `WS` | `/ws/comments/` | События о новых комментариях в реальном времени |

Пример создания комментария:

```json
{
  "user_name": "John123",
  "email": "john@example.com",
  "home_page": "https://example.com",
  "text": "Первый комментарий",
  "parent": null
}
```

Для ответа достаточно передать идентификатор родительского комментария в поле `parent`.

## Обновление production-сервера

После отправки изменений в ветку `develop`:

```bash
git pull origin develop
docker compose -f docker-compose.prod.yml --env-file .env.production build
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python manage.py migrate
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python manage.py collectstatic --noinput
```

Данные PostgreSQL сохраняются в отдельном Docker volume и не удаляются при обычной пересборке или перезапуске контейнеров.

## Безопасность

- Django ORM и сериализаторы DRF исключают построение SQL-запросов из пользовательских строк.
- Серверная валидация обязательных полей выполняется до сохранения комментария.
- Текст комментария фильтруется, чтобы предотвратить XSS.
- Тип, размер и размеры загруженных файлов проверяются сервером.
- Секреты хранятся только в `.env` / `.env.production` и не должны попадать в Git.

