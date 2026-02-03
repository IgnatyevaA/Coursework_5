# Исправление проблемы с .env файлом

## Проблема: "TELEGRAM_BOT_TOKEN не установлен в .env"

Если вы видите эту ошибку, значит файл `.env` либо пустой, либо неправильно отформатирован.

## Решение

### 1. Откройте файл `.env` в редакторе (VS Code)

### 2. Убедитесь, что формат правильный:

**Правильный формат:**
```
TELEGRAM_BOT_TOKEN=8312947286:AAEG59ucCyRVob7Im8Ht8qHixoOsDNPboC8
```

**Неправильный формат (БЕЗ знака =):**
```
TELEGRAM_BOT_TOKEN 8312947286:AAEG59ucCyRVob7Im8Ht8qHixoOsDNPboC8
```

### 3. Полный пример правильного .env файла:

```env
DJANGO_SECRET_KEY=change-me-please-use-32-chars-minimum
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# CORS: укажите домен(ы) фронтенда через запятую
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Telegram
TELEGRAM_BOT_TOKEN=8312947286:AAEG59ucCyRVob7Im8Ht8qHixoOsDNPboC8
```

### 4. Важные правила:

- ✅ **Обязательно** используйте знак `=` между именем переменной и значением
- ✅ **НЕ** ставьте пробелы вокруг знака `=`
- ✅ **НЕ** используйте кавычки вокруг значений (если не нужно)
- ✅ Сохраните файл после редактирования (Ctrl+S)

### 5. После исправления:

1. Сохраните файл (Ctrl+S в VS Code)
2. Перезапустите команду polling:
   ```powershell
   .\.venv\Scripts\python manage.py start_polling
   ```

### 6. Проверка:

Чтобы проверить, что токен загружается правильно, выполните:

```powershell
.\.venv\Scripts\python -c "import os; from dotenv import load_dotenv; from pathlib import Path; load_dotenv(Path('.env')); print('Токен:', os.getenv('TELEGRAM_BOT_TOKEN', 'НЕ НАЙДЕН'))"
```

Если выводится ваш токен — всё правильно! Если "НЕ НАЙДЕН" — проверьте формат файла.
