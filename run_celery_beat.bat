@echo off
REM Запуск Celery Beat для периодических задач
call .venv\Scripts\activate.bat
celery -A config beat -l info
pause
