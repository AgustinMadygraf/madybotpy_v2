"""
Path: src/services/model_config.py
Este módulo contiene una clase que configura el modelo generativo de Gemini AI.
"""

import os
import google.generativeai as genai
from src.logs.config_logger import LoggerConfigurator

# Configuración del logger
logger = LoggerConfigurator().configure()

class ModelConfig:
    """
    Clase para configurar el modelo generativo de Gemini AI.
    """

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("La API Key de Gemini no está configurada en las variables de entorno.")
        logger.info("API Key obtenida correctamente.")
        self._configure_model()

    def _configure_model(self):
        """
        Configura el modelo generativo de Gemini.
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
        logger.info("Modelo generativo configurado correctamente: %s", self.model)

    @staticmethod
    def _load_system_instruction():
        """
        Carga las instrucciones del sistema desde el archivo de configuración.
        """
        instruction_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'system_instruction.txt')
        instruction_file_path = os.path.abspath(instruction_file_path)
        logger.info("Buscando instrucciones del sistema en: %s", instruction_file_path)

        try:
            with open(instruction_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error("Error: El archivo system_instruction.txt no se encontró.")
            raise FileNotFoundError("El archivo system_instruction.txt no se encuentra en la ruta especificada.")
