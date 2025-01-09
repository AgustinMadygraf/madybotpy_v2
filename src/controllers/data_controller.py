"""
Path: src/controllers/data_controller.py
"""

import os
from flask import Blueprint, request, redirect
from flask_cors import CORS
from marshmallow import ValidationError
from dotenv import load_dotenv
from src.views.data_view import render_json_response
from src.logs.config_logger import LoggerConfigurator
from src.services.data_validator import DataSchemaValidator
from src.services.response_generator import ResponseGenerator

# Configuración del logger
logger = LoggerConfigurator().configure()

load_dotenv()

# Crear un blueprint para el controlador
data_controller = Blueprint('data_controller', __name__)
CORS(data_controller)

# Instancias de servicios
data_validator = DataSchemaValidator()
response_generator = ResponseGenerator()

@data_controller.route('/', methods=['GET'])
def redirect_to_frontend():
    "Redirige a la URL del frontend."
    url_frontend = os.getenv('URL_FRONTEND')
    return redirect(url_frontend)

@data_controller.route('/None', methods=['GET'])
def redirect_to_frontend_none():
    "Redirige a la URL del frontend."
    url_frontend = os.getenv('URL_FRONTEND')
    return redirect(url_frontend)

@data_controller.route('/receive-data', methods=['GET', 'POST', 'HEAD'])
def receive_data():
    "Recibe un mensaje y un ID de usuario y responde con un JSON."
    if request.method == 'HEAD':
        return '', 200

    if request.method == 'GET':
        url_frontend = os.getenv('URL_FRONTEND')
        return redirect(url_frontend)
    try:
        logger.info("Request JSON: \n| %s \n", request.json)
        data = data_validator.validate(request.json)
        logger.info("Datos validados: %s", data)
    except ValidationError as err:
        logger.warning("Error de validación en la solicitud: %s", err.messages)
        message_output = "Datos inválidos en la solicitud."
        return render_json_response(400, message_output, stream=False)
    try:
        # Verificar el valor de 'stream' en el JSON de la solicitud
        if data.get('stream'):
            logger.info("Generando respuesta en modo streaming.")
            # Usar generate_response_streaming si 'stream' es True
            message_output = ''.join(response_generator.generate_response_streaming(data['prompt_user']))
        else:
            logger.info("Generando respuesta en modo normal.")
            # Usar generate_response si 'stream' es None o False
            message_output = response_generator.generate_response(data['prompt_user'])
        code = 200
    except (ConnectionError, TimeoutError) as e:
        message_output = "Error de conexión al generar la respuesta."
        logger.error("Error de conexión: %s", e)
        code = 503  # Servicio no disponible
    except RuntimeError as e:
        message_output = "Error de ejecución en el generador de respuesta."
        logger.error("Error de ejecución: %s", e)
        code = 500
    except Exception as e:  # pylint: disable=W0718
        message_output = "Error desconocido en la generación de la respuesta."
        logger.error("Error no anticipado: %s", e)
        code = 500
    logger.info("Generated: \n| %s", message_output)
    return render_json_response(code, message_output, stream=False)

@data_controller.route('/health-check', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado del servidor.
    """
    logger.info("Health check solicitado. El servidor está funcionando correctamente.")
    return render_json_response(200, "El servidor está operativo.")
