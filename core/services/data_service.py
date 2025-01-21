"""
Path: core/services/data_service.py
Servicio para manejar la lógica principal de recepción y procesamiento de datos.
"""

from marshmallow import ValidationError
from core.logs.config_logger import LoggerConfigurator
from core.services.data_validator import DataSchemaValidator
from core.services.response_generator import ResponseGenerator
from core.channels.imessaging_channel import IMessagingChannel

logger = LoggerConfigurator().configure()

class DataService:
    """
    Servicio que encapsula la lógica de validación y generación de respuesta,
    desacoplándola del framework Flask.
    """

    def __init__(self, validator: DataSchemaValidator, response_generator: ResponseGenerator, channel: IMessagingChannel):
        self.validator = validator
        self.response_generator = response_generator
        self.channel = channel

    def process_incoming_data(self, json_data: dict) -> str:
        """
        Valida los datos entrantes, obtiene el mensaje y decide si la respuesta
        se genera en streaming o de forma normal.
        Retorna el mensaje de respuesta final para ser renderizado.
        """

        # Validar
        logger.info("Validando datos: %s", json_data)
        try:
            valid_data = self.validator.validate(json_data)
        except ValidationError as err:
            logger.warning("Error de validación: %s", err.messages)
            raise

        # Recibir mensaje desde el canal
        processed_data = self.channel.receive_message(valid_data)
        logger.info("Datos procesados desde el canal: %s", processed_data)

        message_text = processed_data.get('message')
        is_stream = processed_data.get('stream', False)

        try:
            if is_stream:
                logger.info("Generando respuesta en modo streaming.")
                return self.response_generator.generate_response_streaming(message_text)
            else:
                logger.info("Generando respuesta en modo normal.")
                return self.response_generator.generate_response(message_text)
        except Exception as e:
            logger.error("Error procesando la solicitud: %s", e)
            raise
