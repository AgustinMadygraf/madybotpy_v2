REM Path: gunicorn_starter.bat
@echo off
pipenv run gunicorn --bind 0.0.0.0:5000 main:app
