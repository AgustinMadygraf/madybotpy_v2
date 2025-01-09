REM Path: gunicorn_starter.bat
@echo off
gunicorn --bind 0.0.0.0:5000 main:app
