"""
Path: src/services/response_generator.py
Este módulo contiene una clase que genera respuestas utilizando un modelo de lenguaje generativo.
"""

from src.logs.config_logger import LoggerConfigurator
from src.services.model_config import ModelConfig

# Configuración del logger
logger = LoggerConfigurator().configure()

class ResponseGenerator:
    """
    Clase que genera respuestas utilizando un modelo de lenguaje generativo.
    """

    def __init__(self, model_config: ModelConfig):
        """
        Constructor que recibe una instancia de ModelConfig.
        """
        self.model_config = model_config
        self.model = self.model_config.model
        logger.info("ResponseGenerator inicializado con el modelo configurado.")

    def generate_response(self, message_input):
        """
        Genera una respuesta en base al mensaje de entrada.
        """
        logger.info("Generando respuesta para el mensaje: %s", message_input)
        self._start_chat_session()
        try:
            response = self.chat_session.send_message(message_input)
            logger.info("Respuesta generada: %s", response.text)
            return response.text
        except Exception as e:
            logger.error("Error durante la generación de la respuesta: %s", e)
            raise

    def generate_response_streaming(self, message_input, chunk_size=30):
        """
        Genera una respuesta en bloques de texto.
        """
        logger.info("Generando respuesta en modo streaming para el mensaje: %s", message_input)
        self._start_chat_session()
        response = self.chat_session.send_message(message_input)
        offset = 0
        full_response = ""
        while offset < len(response.text):
            chunk = response.text[offset:offset + chunk_size]
            full_response += chunk
            logger.info("Chunk generado: %s", chunk)
            offset += chunk_size
        return full_response

    def _start_chat_session(self):
        """
        Inicia una nueva sesión de chat si no existe una.
        """
        if not hasattr(self, 'chat_session'):
            self.chat_session = self.model.start_chat()
            logger.info("Sesión de chat iniciada.")
