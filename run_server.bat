@echo off
REM Запуск Django сервера
call .venv\Scripts\activate.bat
python manage.py runserver
pause
