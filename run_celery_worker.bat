@echo off
REM Запуск Celery Worker (Windows)
call .venv\Scripts\activate.bat
celery -A config worker -l info --pool=solo
pause
