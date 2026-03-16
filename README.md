## Atomic Habits Tracker (backend)

SPA-бэкенд для трекера полезных привычек (DRF + JWT + Celery + Telegram).

### Запуск через Docker (одной командой)

- **1) Создать `.env`**:

Локально можно взять `env.example` (для Docker важно, чтобы были PostgreSQL переменные и Redis URL). Самый простой вариант:

```bash
copy env.example .env
```

И поменять в `.env`:

- `POSTGRES_HOST=db`
- `CELERY_BROKER_URL=redis://redis:6379/0`
- `CELERY_RESULT_BACKEND=redis://redis:6379/0`

- **2) Запустить проект**:

```bash
docker compose up --build
```

После старта API будет доступен на `http://localhost/` (через nginx).

### Быстрый старт (Windows / PowerShell)

- **1) Установить зависимости**:

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

- **2) Создать `.env`**:

Скопируйте `env.example` в `.env` и заполните значения:

- `DJANGO_SECRET_KEY` (желательно 32+ символа)
- `CORS_ALLOWED_ORIGINS` (URL фронтенда через запятую, например: `http://localhost:3000,http://localhost:8080`)
- `TELEGRAM_BOT_TOKEN` (токен бота от @BotFather)
- `CELERY_BROKER_URL` (по умолчанию `redis://localhost:6379/0`)

- **3) Миграции**:

```bash
.\.venv\Scripts\python manage.py migrate
```

- **4) Запуск API**:

**Вариант 1 (через скрипт - PowerShell)**:
```powershell
.\run_server.ps1
```

**Вариант 2 (через скрипт - CMD)**:
```cmd
run_server.bat
```

**Вариант 3 (вручную)**:
```bash
.\.venv\Scripts\python manage.py runserver
```

API будет доступен на `http://127.0.0.1:8000/`

### Документация

- Swagger UI: `/api/docs/`
- OpenAPI schema: `/api/schema/`

### Celery + напоминания в Telegram

Задача напоминаний запускается раз в минуту через Celery Beat

**Важно**: Перед запуском Celery убедитесь, что Redis запущен локально (по умолчанию `redis://localhost:6379/0`).

- **Worker (Windows)**:

**Вариант 1 (через скрипт)**:
```bash
.\run_celery_worker.bat
```

**Вариант 2 (вручную)**:
```bash
celery -A config worker -l info --pool=solo
```

- **Beat** (в отдельном терминале):

**Вариант 1 (через скрипт)**:
```bash
.\run_celery_beat.bat
```

**Вариант 2 (вручную)**:
```bash
celery -A config beat -l info
```

### Тестирование Telegram интеграции

Для проверки отправки сообщений в Telegram используйте management команду:

```bash
.\.venv\Scripts\python manage.py test_telegram <chat_id> "Тестовое сообщение"
```

**Как получить chat_id**:
1. Найдите бота в Telegram: `https://t.me/<ваш_бот>`
2. Начните диалог с ботом
3. Отправьте любое сообщение боту
4. Используйте API Telegram: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Найдите `chat.id` в ответе

### Основные эндпоинты

- **Регистрация**: `POST /api/auth/register/`
- **Авторизация (JWT)**: `POST /api/auth/token/`
- **Refresh**: `POST /api/auth/token/refresh/`
- **Указать Telegram chat_id**: `PATCH /api/users/me/telegram/`
- **Привычки (только свои)**: CRUD `/api/habits/`
- **Публичные привычки**: `GET /api/habits/public/`

### Тесты и качество

**Запуск тестов с покрытием**:
```bash
.\.venv\Scripts\pytest --cov=. --cov-report=term-missing
```

**Проверка кода (flake8)**:
```bash
.\.venv\Scripts\python -m flake8 .
```

**Текущее покрытие**: ~90% (требование: ≥80%)

**Flake8**: 100% (миграции исключены)

### Создание суперпользователя (для админки)

```bash
.\.venv\Scripts\python manage.py createsuperuser
```

Админка доступна на: `http://127.0.0.1:8000/admin/`

---

## CI/CD и деплой на сервер (GitHub Actions + Docker Compose)

### Адрес сервера

Развернутое приложение: **`http://<SERVER_IP>/`** (замените на ваш адрес после деплоя).

### Что деплоится

- Контейнеры: **Django (gunicorn)**, **PostgreSQL**, **Redis**, **Celery worker**, **Celery beat**, **nginx**
- Прод-оркестрация: `docker-compose.prod.yml`
- Образ приложения пушится в **GHCR**: `ghcr.io/<owner>/<repo>:sha-...`

### Настройка сервера (Yandex Cloud VM)

- **1) Установить Docker + Compose plugin** (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

- **2) Подготовить директорию деплоя**:

```bash
mkdir -p ~/apps/coursework_5
cd ~/apps/coursework_5
```

- **3) Создать `.env` на сервере**:

Скопируйте `env.prod.example` в `.env` и заполните значения:

```bash
cp env.prod.example .env
nano .env
```

### Настройка GitHub Secrets (для workflow `Deploy`)

В репозитории GitHub → Settings → Secrets and variables → Actions добавьте:

- **`SSH_HOST`**: IP/домен сервера
- **`SSH_PORT`**: порт SSH (обычно `22`)
- **`SSH_USER`**: пользователь (например, `ubuntu`)
- **`SSH_KEY`**: приватный ключ (PEM) для подключения по SSH
- **`DEPLOY_PATH`**: путь на сервере (например, `/home/ubuntu/apps/coursework_5`)

### Как работает деплой

- Workflow `CI` запускается на PR/пуш в `develop`: **flake8 + pytest + docker build**
- Workflow `Deploy` запускается на push в `develop`:
  - собирает и пушит образ в GHCR
  - копирует `docker-compose.prod.yml` и nginx-конфиг на сервер
  - делает `docker compose pull` и `docker compose up -d --remove-orphans`
