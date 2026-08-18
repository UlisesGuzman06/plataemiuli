@echo off
echo Iniciando Plata Emi y Uli...
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe manage.py runserver 8000
) else if exist "..\Proyectos Propios\plata_emi_uli\.venv\Scripts\python.exe" (
    "..\Proyectos Propios\plata_emi_uli\.venv\Scripts\python.exe" manage.py runserver 8000
) else (
    python manage.py runserver 8000
)
pause
