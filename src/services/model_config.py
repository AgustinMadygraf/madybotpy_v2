"""
Path: src/services/model_config.py
Factory o configuración para crear instancias de clientes LLM (Gemini u otros).
"""

import os
from src.logs.config_logger import LoggerConfigurator
from src.services.llm_impl.gemini_llm import GeminiLLMClient

logger = LoggerConfigurator().configure()

class ModelConfig:
    """
    Carga la configuración necesaria (API key, system instruction) y
    crea la instancia concreta de LLMClient.
    """

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("La API Key de Gemini no está configurada en las variables de entorno.")

        logger.info("API Key de Gemini obtenida correctamente.")
        self.system_instruction = self._load_system_instruction()

    def create_llm_client(self):
        """
        Crea y retorna una instancia de GeminiLLMClient utilizando
        la configuración actual.
        """
        return GeminiLLMClient(self.api_key, self.system_instruction)

    def _load_system_instruction(self):
        """
        Carga las instrucciones del sistema desde el archivo system_instruction.txt.
        """
        import os
        instruction_file_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'config', 'system_instruction.txt'
        )
        instruction_file_path = os.path.abspath(instruction_file_path)
        logger.info("Buscando instrucciones del sistema en: %s", instruction_file_path)

        try:
            with open(instruction_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error("Error: El archivo system_instruction.txt no se encontró.")
            raise FileNotFoundError("El archivo system_instruction.txt no se encuentra en la ruta especificada.")
