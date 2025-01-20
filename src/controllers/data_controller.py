"""
Path: src/controllers/data_controller.py
Controlador Flask que se encarga de recibir las peticiones HTTP y delegar
la lógica a DataService.
"""

import os
from flask import Blueprint, request, redirect
from flask_cors import CORS
from dotenv import load_dotenv
from marshmallow import ValidationError
from src.views.data_view import render_json_response
from src.logs.config_logger import LoggerConfigurator

# Services y canales
from src.services.data_service import DataService
from src.services.data_validator import DataSchemaValidator
from src.services.model_config import ModelConfig
from src.services.response_generator import ResponseGenerator
from src.channels.imessaging_channel import IMessagingChannel

logger = LoggerConfigurator().configure()
load_dotenv()

data_controller = Blueprint('data_controller', __name__)
CORS(data_controller)

# Implementación simple de canal (web) para mensajes
class WebMessagingChannel(IMessagingChannel):
    def send_message(self, msg: str, chat_id: str = None) -> None:
        logger.info("Mensaje enviado al usuario web: %s", msg)

    def receive_message(self, payload: dict) -> dict:
        logger.info("Mensaje recibido desde la interfaz web: %s", payload)
        return {
            "message": payload.get('prompt_user'),
            "stream": payload.get('stream', False)
        }

# Instanciar servicios y canal
web_channel = WebMessagingChannel()
data_validator = DataSchemaValidator()

# Crear cliente LLM y ResponseGenerator
model_config = ModelConfig()
llm_client = model_config.create_llm_client()
response_generator = ResponseGenerator(llm_client)

# Crear DataService que unifica validación y respuesta
data_service = DataService(
    validator=data_validator,
    response_generator=response_generator,
    channel=web_channel
)

root_API = os.getenv('ROOT_API', '/')

@data_controller.route(root_API, methods=['GET'])
def redirect_to_frontend():
    url_frontend = os.getenv('URL_FRONTEND')
    return redirect(url_frontend)

@data_controller.route(root_API + 'receive-data', methods=['GET', 'POST', 'HEAD'])
def receive_data():
    if request.method == 'HEAD':
        return '', 200

    if request.method == 'GET':
        url_frontend = os.getenv('URL_FRONTEND')
        return redirect(url_frontend)

    try:
        logger.info("Request JSON: \n| %s \n", request.json)
        # Procesar la data con nuestro DataService
        response_message = data_service.process_incoming_data(request.json)
        return render_json_response(200, response_message, stream=False)

    except ValidationError:
        return render_json_response(400, "Datos inválidos en la solicitud.", stream=False)
    except Exception as e:
        logger.error("Error procesando la solicitud: %s", e)
        return render_json_response(500, "Error procesando la solicitud.", stream=False)

@data_controller.route(root_API + 'health-check', methods=['GET'])
def health_check():
    logger.info("Health check solicitado. El servidor está funcionando correctamente.")
    return render_json_response(200, "El servidor está operativo.")
