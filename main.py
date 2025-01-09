"""
Path: main.py

"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from src.controllers.data_controller import data_controller
from src.logs.config_logger import LoggerConfigurator

# Configuración del logger al inicio del script
logger = LoggerConfigurator().configure()
logger.debug("Logger configurado correctamente al inicio del servidor.")

# Cargar variables de entorno desde el archivo .env
try:
    logger.debug("Intentando cargar el archivo .env")
    if not load_dotenv():
        raise FileNotFoundError(".env file not found")
    logger.debug(".env file cargado correctamente")
except FileNotFoundError as e:
    logger.error("Error loading .env file: %s", e)
    logger.debug("Asegúrate de que el archivo .env existe en el directorio raíz del proyecto")
    print("Please create a .env file with the necessary environment variables.")
    exit(1)

app = Flask(__name__)
CORS(app)

# Registrar el blueprint del controlador
try:
    app.register_blueprint(data_controller)
    logger.info("Blueprint registrado correctamente.")
except Exception as e:
    logger.error("Error al registrar el blueprint: %s", e)
    exit(1)


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
        logger.info("Servidor configurado para HTTP.")
    except Exception as e:
        logger.error("Error al iniciar el servidor Flask: %s", e)
        exit(1)
