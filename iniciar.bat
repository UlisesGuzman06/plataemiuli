@echo off
echo Iniciando Plata Emi y Uli...
cd /d "%~dp0"
.venv\Scripts\python.exe manage.py runserver 8000
pause
