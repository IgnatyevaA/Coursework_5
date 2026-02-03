# Настройка Telegram бота

## Проблема: бот не отвечает на `/start`

Если бот не отвечает на команды, нужно настроить либо webhook, либо polling.

## Решение 1: Polling (рекомендуется для локальной разработки)

**Polling не требует туннеля или публичного URL** — просто запускает процесс, который периодически проверяет новые сообщения.

1. **Запустите Django сервер** (в одном терминале):

   **В PowerShell:**
   ```powershell
   .\run_server.ps1
   ```
   
   **В CMD:**
   ```cmd
   run_server.bat
   ```
   
   **Или вручную:**
   ```bash
   .\.venv\Scripts\python manage.py runserver
   ```

2. **Запустите polling** (в другом терминале):

   **В PowerShell:**
   ```powershell
   .\run_telegram_polling.ps1
   ```
   
   **В CMD:**
   ```cmd
   run_telegram_polling.bat
   ```
   
   **Или вручную:**
   ```bash
   .\.venv\Scripts\python manage.py start_polling
   ```

3. **Готово!** Теперь отправьте `/start` боту в Telegram — он должен ответить!

**Преимущества polling:**
- Не требует туннеля (ngrok и т.д.)
- Работает локально без публичного URL
- Проще настроить

**Недостатки:**
- Нужно держать процесс запущенным
- Менее эффективен для продакшена

## Решение 2: Webhook (для продакшена)

### Для локальной разработки (через ngrok)

1. **Установите ngrok**: https://ngrok.com/download

2. **Запустите Django сервер**:
   ```bash
   .\run_server.bat
   ```

3. **В отдельном терминале запустите ngrok**:
   ```bash
   ngrok http 8000
   ```

4. **Скопируйте HTTPS URL** из ngrok (например, `https://abc123.ngrok.io`)

5. **Установите webhook**:
   ```bash
   .\.venv\Scripts\python manage.py set_webhook --url https://abc123.ngrok.io/api/telegram/webhook/
   ```

6. **Проверьте**: отправьте `/start` боту в Telegram — он должен ответить!

### Для продакшена

```bash
.\.venv\Scripts\python manage.py set_webhook --url https://yourdomain.com/api/telegram/webhook/
```

## Что делает команда `/start`

Когда пользователь отправляет `/start`:
- Бот получает его Chat ID
- Если у пользователя есть аккаунт с таким же username в системе, Chat ID сохраняется автоматически
- Если аккаунта нет, бот отправляет инструкцию, как зарегистрироваться и указать Chat ID

## Удаление webhook

Если нужно удалить webhook (например, для переключения на polling):

```bash
.\.venv\Scripts\python manage.py delete_webhook
```

## Проверка статуса webhook

Можно проверить через Telegram API:

```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

Или использовать команду `set_webhook` без параметров — она покажет текущий статус.
