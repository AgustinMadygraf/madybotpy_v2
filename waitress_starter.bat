REM Path: waitress_starter.bat
@echo off
REM Iniciar Waitress en el puerto 5000
pipenv run waitress-serve --host=0.0.0.0 --port=5000 main:app