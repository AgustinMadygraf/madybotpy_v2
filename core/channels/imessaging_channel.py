"""
Path: core/channels/imessaging_channel.py
Definición de la interfaz abstracta para los canales de mensajería.
"""

from abc import ABC, abstractmethod

class IMessagingChannel(ABC):
    """
    Interfaz para los canales de mensajería. Define los métodos básicos que
    deben implementar las clases concretas para manejar la comunicación.
    """

    @abstractmethod
    def send_message(self, msg: str, chat_id: str = None) -> None:
        """
        Enviar un mensaje al usuario a través del canal.
        
        :param msg: El mensaje a enviar.
        :param chat_id: El ID del destinatario (opcional, dependiendo del canal).
        """
        pass

    @abstractmethod
    def receive_message(self, payload: dict) -> dict:
        """
        Procesar un mensaje entrante del canal.
        
        :param payload: Un diccionario con los datos del mensaje recibido.
        :return: Un diccionario procesado listo para ser utilizado.
        """
        pass
