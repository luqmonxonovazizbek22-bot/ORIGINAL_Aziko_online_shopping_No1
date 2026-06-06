@echo off
cd /d %~dp0
if not exist .venv (
    py -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
pause
