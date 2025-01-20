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
from src.services.model_config import ModelConfig
from src.channels.imessaging_channel import IMessagingChannel

# Configuración del logger
logger = LoggerConfigurator().configure()

# Cargar variables de entorno
load_dotenv()

# Crear un blueprint para el controlador
data_controller = Blueprint('data_controller', __name__)
CORS(data_controller)

# Instancias de servicios
data_validator = DataSchemaValidator()
model_config = ModelConfig()
response_generator = ResponseGenerator(model_config)

# Ejemplo de implementación de un canal de mensajería (solo para web por ahora)
class WebMessagingChannel(IMessagingChannel):
    """
    Clase concreta para manejar mensajes desde la interfaz web.
    """

    def send_message(self, msg: str, chat_id: str = None) -> None:
        """
        Envía un mensaje de respuesta al usuario de la web (no se necesita chat_id).
        """
        logger.info("Mensaje enviado al usuario web: %s", msg)

    def receive_message(self, payload: dict) -> dict:
        """
        Procesa el mensaje entrante desde la interfaz web.
        """
        logger.info("Mensaje recibido desde la interfaz web: %s", payload)
        return {
            "message": payload.get('prompt_user'),
            "stream": payload.get('stream', False)
        }

# Instancia del canal web
web_channel = WebMessagingChannel()

root_API = os.getenv('ROOT_API', '/')

@data_controller.route(root_API, methods=['GET'])
def redirect_to_frontend():
    """
    Redirige a la URL del frontend.
    """
    url_frontend = os.getenv('URL_FRONTEND')
    return redirect(url_frontend)

@data_controller.route(root_API + 'receive-data', methods=['GET', 'POST', 'HEAD'])
def receive_data():
    """
    Recibe un mensaje y un ID de usuario y responde con un JSON.
    """
    if request.method == 'HEAD':
        return '', 200

    if request.method == 'GET':
        url_frontend = os.getenv('URL_FRONTEND')
        return redirect(url_frontend)

    try:
        logger.info("Request JSON: \n| %s \n", request.json)
        # Validar y procesar el mensaje recibido a través del canal
        data = data_validator.validate(request.json)
        processed_data = web_channel.receive_message(data)
        logger.info("Datos procesados del canal web: %s", processed_data)
    except ValidationError as err:
        logger.warning("Error de validación en la solicitud: %s", err.messages)
        return render_json_response(400, "Datos inválidos en la solicitud.", stream=False)

    try:
        if processed_data.get('stream'):
            logger.info("Generando respuesta en modo streaming.")
            message_output = ''.join(response_generator.generate_response_streaming(processed_data['message']))
        else:
            logger.info("Generando respuesta en modo normal.")
            message_output = response_generator.generate_response(processed_data['message'])
        return render_json_response(200, message_output, stream=False)
    except Exception as e:
        logger.error("Error procesando la solicitud: %s", e)
        return render_json_response(500, "Error procesando la solicitud.", stream=False)

@data_controller.route(root_API + 'health-check', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado del servidor.
    """
    logger.info("Health check solicitado. El servidor está funcionando correctamente.")
    return render_json_response(200, "El servidor está operativo.")
