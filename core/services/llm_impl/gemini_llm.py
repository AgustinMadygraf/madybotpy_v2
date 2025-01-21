"""
Path: core/services/llm_impl/gemini_llm.py
Implementación de ILLMClient utilizando la API de Gemini.
"""

import google.generativeai as genai
from core.services.llm_client import ILLMClient
from core.logs.config_logger import LoggerConfigurator

logger = LoggerConfigurator().configure()

class GeminiLLMClient(ILLMClient):
    def __init__(self, api_key: str, system_instruction: str):
        """
        Inicializa el cliente para Gemini, configurando la API key y el modelo.
        """
        self.api_key = api_key
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
            system_instruction=system_instruction
        )

        # Sesión de chat (se inicia en "lazy mode")
        self.chat_session = None
        logger.info("GeminiLLMClient inicializado correctamente.")

    def send_message(self, message: str) -> str:
        """
        Envía un mensaje al modelo y retorna la respuesta en texto.
        """
        self._start_chat_session()
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            logger.error("Error al enviar mensaje a Gemini: %s", e)
            raise

    def send_message_streaming(self, message: str, chunk_size: int = 30) -> str:
        """
        Envía un mensaje al modelo y retorna la respuesta en modo streaming.
        Se va acumulando en un string final.
        """
        self._start_chat_session()
        try:
            response = self.chat_session.send_message(message)
            full_response = ""
            offset = 0
            while offset < len(response.text):
                chunk = response.text[offset:offset + chunk_size]
                full_response += chunk
                offset += chunk_size
            return full_response
        except Exception as e:
            logger.error("Error durante la respuesta streaming en Gemini: %s", e)
            raise

    def _start_chat_session(self):
        """
        Inicia la sesión de chat si no existe.
        """
        if not self.chat_session:
            self.chat_session = self.model.start_chat()
            logger.info("Sesión de chat iniciada con el modelo Gemini.")
