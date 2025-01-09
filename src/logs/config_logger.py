"""
src/logs/config_logger.py
Logger configuration module.
"""

import logging.config
import os
import json
from abc import ABC, abstractmethod
from src.logs.info_error_filter import InfoErrorFilter
from dotenv import load_dotenv
import sys

# Cargar las variables de entorno desde .env
load_dotenv()

class ConfigStrategy(ABC):
    """Abstract base class for configuration strategies."""
    @abstractmethod
    def load_config(self):
        """Loads configuration from a specific source."""
        print("load_config method not implemented.")

class JSONConfigStrategy(ConfigStrategy):
    """Loads configuration from a JSON file."""
    def __init__(self, config_path='src/logs/logging.json', env_key='LOG_CFG'):
        self.config_path = config_path
        self.env_key = env_key

    def load_config(self):
        """Loads configuration from a JSON file or environment variable."""
        path = self.config_path
        value = os.getenv(self.env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt', encoding='utf-8') as f:
                return json.load(f)
        return None

class LoggerConfigurator:
    """Configures logging for the application using a strategy pattern."""
    def __init__(self, config_strategy=None, default_level=logging.INFO):
        self.config_strategy = config_strategy or JSONConfigStrategy()
        self.default_level = default_level

    def configure(self):
        """Configures the logger using the provided strategy."""
        config = self.config_strategy.load_config()
        # Cargar la variable IS_DEVELOPMENT desde el entorno
        is_development_str = os.getenv('IS_DEVELOPMENT', 'false').lower()
        is_development = is_development_str == 'true'

        if config:
            # Modificar la configuración del handler 'console' basado en IS_DEVELOPMENT
            handlers = config.get('handlers', {})
            console_handler = handlers.get('console', None)
            if console_handler:
                if is_development:
                    # En desarrollo, permitir DEBUG
                    console_handler['level'] = 'DEBUG'
                else:
                    # En producción, establecer al menos INFO
                    console_handler['level'] = 'INFO'
            else:
                # Si no existe un handler 'console', podrías agregar uno si es necesario
                if is_development:
                    config['handlers']['console'] = {
                        "class": "logging.StreamHandler",
                        "level": "DEBUG",
                        "formatter": "simpleFormatter"
                    }
                    # Agregar el handler a los loggers
                    for logger_name, logger_info in config.get('loggers', {}).items():
                        logger_info['handlers'].append('console')
                else:
                    # En producción, podrías optar por no agregar el handler 'console' o ajustarlo
                    pass

            logging.config.dictConfig(config)
        else:
            # Configuración por defecto si no se encuentra el archivo de logging.json
            logging.basicConfig(level=self.default_level)
            logging.warning("Logging configuration file not found. Using default settings.")

        return logging.getLogger(__name__)

# Configuración inicial del logger para módulos individuales
initial_config_strategy = JSONConfigStrategy()
logger_configurator = LoggerConfigurator(config_strategy=initial_config_strategy)
logger = logger_configurator.configure()
logger.addFilter(InfoErrorFilter())  # Aplica el filtro InfoErrorFilter

# Configurar el StreamHandler para usar UTF-8 (si es necesario)
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setEncoding('utf-8')
