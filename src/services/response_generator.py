# Path: src/services/response_generator.py
"""
Este módulo contiene una clase que genera respuestas utilizando un modelo de lenguaje generativo.
"""

import os
import time
import google.generativeai as genai
from src.views.data_view import render_json_response
from src.logs.config_logger import LoggerConfigurator

# Configuración del logger
logger = LoggerConfigurator().configure()

class ResponseGenerator:
    """
    ResponseGenerator es una clase que genera respuestas utilizando el modelo Gemini AI.
    """

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        logger.info("API Key obtenida: %s", self.api_key)
        self._configure_model()

    def _configure_model(self):
        """
        Configura el modelo generativo con la API Key y las instrucciones del sistema.
        """
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            },
            system_instruction=self._load_system_instruction(),
        )
        logger.info("Modelo generativo configurado: %s", self.model)

    @staticmethod
    def _load_system_instruction():
        """
        Carga las instrucciones del sistema desde el archivo system_instruction.txt.
        """
        instruction_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'system_instruction.txt')
        instruction_file_path = os.path.abspath(instruction_file_path)
        logger.info("Buscando system_instruction.txt en: %s", instruction_file_path)

        try:
            with open(instruction_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error("Error: El archivo system_instruction.txt no se encontró.")
            return "Error: El archivo system_instruction.txt no se encontró."

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
        Genera una respuesta en base al mensaje de entrada, en bloques de texto.
        """
        logger.info("Generando respuesta en modo streaming para el mensaje: %s", message_input)
        self._start_chat_session()
        response = self.chat_session.send_message(message_input)
        offset = 0
        full_response = ""
        while offset < len(response.text):
            chunk = response.text[offset:offset + chunk_size]
            full_response += chunk
            self.clear_console()
            render_json_response(code=200, message=full_response, stream=True)
            offset += chunk_size
            time.sleep(0.001)
        yield full_response

    def _start_chat_session(self):
        """
        Inicia una nueva sesión de chat si no existe una.
        """
        if not hasattr(self, 'chat_session'):
            self.chat_session = self.model.start_chat()
            logger.info("Sesión de chat iniciada.")

    @staticmethod
    def clear_console():
        """
        Limpia la consola según el sistema operativo.
        """
        os.system('cls' if os.name == 'nt' else 'clear')