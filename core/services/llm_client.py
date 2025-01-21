"""
Path: core/services/llm_client.py
Interfaz ILLMClient para clientes LLM.
"""

from abc import ABC, abstractmethod

class ILLMClient(ABC):
    @abstractmethod
    def send_message(self, message: str) -> str:
        """
        Envía un mensaje al modelo LLM y retorna la respuesta completa en texto.
        """
        pass

    @abstractmethod
    def send_message_streaming(self, message: str, chunk_size: int = 30) -> str:
        """
        Envía un mensaje al modelo LLM y retorna la respuesta
        en modo streaming (concatenada finalmente).
        """
        pass
