"""
Path: core/services/response_generator.py
Este módulo contiene una clase que genera respuestas utilizando un modelo de lenguaje generativo,
manteniendo la lógica independiente de cualquier canal específico (web, Telegram, etc.).
"""

from core.logs.config_logger import LoggerConfigurator
from core.services.model_config import ModelConfig

# Configuración del logger
logger = LoggerConfigurator().configure()

class ResponseGenerator:
    """
    Clase que genera respuestas utilizando un modelo de lenguaje generativo.
    """

    def __init__(self, model_config: ModelConfig):
        """
        Constructor que recibe una instancia de ModelConfig.
        
        :param model_config: Instancia de la clase ModelConfig que contiene
                             la configuración del modelo generativo.
        """
        self.model_config = model_config
        self.model = self.model_config.model
        logger.info("ResponseGenerator inicializado con el modelo configurado.")

    def generate_response(self, message_input: str) -> str:
        """
        Genera una respuesta en base al mensaje de entrada, sin preocuparse
        por el canal desde el que proviene.

        :param message_input: El texto del mensaje de entrada.
        :return: El texto de la respuesta generada por el modelo.
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

    def generate_response_streaming(self, message_input: str, chunk_size: int = 30) -> str:
        """
        Genera una respuesta en bloques de texto (streaming). La función retorna todo el texto al final,
        pero internamente se divide en pequeños trozos para simular una lógica de streaming.
        
        :param message_input: El texto del mensaje de entrada.
        :param chunk_size: Tamaño de cada bloque que se lee del texto.
        :return: Todo el texto de la respuesta generada, concatenado.
        """
        logger.info("Generando respuesta en modo streaming para el mensaje: %s", message_input)
        self._start_chat_session()
        response = self.chat_session.send_message(message_input)

        offset = 0
        full_response = ""
        while offset < len(response.text):
            chunk = response.text[offset:offset + chunk_size]
            full_response += chunk
            # Loguea cada chunk para fines de debug, sin limpiar consola
            logger.debug("Chunk generado: %s", chunk)
            offset += chunk_size

        logger.info("Respuesta completa (streaming simulada): %s", full_response)
        return full_response

    def _start_chat_session(self) -> None:
        """
        Inicia una nueva sesión de chat si no existe una.
        """
        if not hasattr(self, 'chat_session'):
            self.chat_session = self.model.start_chat()
            logger.info("Sesión de chat iniciada con el modelo generativo.")
