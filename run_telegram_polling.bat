@echo off
REM Запуск Telegram polling (альтернатива webhook, не требует туннеля)
call .venv\Scripts\activate.bat
python manage.py start_polling
pause
