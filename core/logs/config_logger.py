"""
Path: core/logs/config_logger.py
Clase LoggerConfigurator mejorada para garantizar una única instancia y configuración consistente.
"""

import os
import json
import logging.config
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path


class ConfigStrategy(ABC):
    """Clase base para las estrategias de configuración del logger."""
    
    @abstractmethod
    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        Carga y retorna la configuración del logger.

        Returns:
            Optional[Dict[str, Any]]: Configuración del logger o None si no se puede cargar.
        """
        ...


class JSONConfigStrategy(ConfigStrategy):
    """Estrategia para cargar la configuración desde un archivo JSON con soporte para diferentes entornos."""
    
    def __init__(self, config_path: str = 'core/logs/logging.json'):
        """
        Inicializa la estrategia JSON con la ruta del archivo de configuración.

        Args:
            config_path (str): Ruta al archivo de configuración JSON.
        """
        self.config_path = Path(config_path)
        self._validate_config_path()
    
    def _validate_config_path(self) -> None:
        """Valida que la ruta del archivo de configuración sea correcta."""
        if not self.config_path.is_absolute():
            # Convertir ruta relativa a absoluta desde la raíz del proyecto.
            self.config_path = Path(os.path.dirname(__file__)).parent.parent / self.config_path
    
    def _adjust_log_level(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ajusta los niveles de log y elimina handlers no deseados según el entorno.

        Args:
            config (Dict[str, Any]): Configuración original.

        Returns:
            Dict[str, Any]: Configuración ajustada.
        """
        is_development = os.getenv('IS_DEVELOPMENT', 'true').lower() == 'true'

        # Ajustar nivel de log para el handler de consola
        if 'handlers' in config and 'console' in config['handlers']:
            config['handlers']['console']['level'] = 'DEBUG' if is_development else 'INFO'

        # Ajustar nivel de log para el root logger
        if 'loggers' in config and '' in config['loggers']:
            config['loggers']['']['level'] = 'DEBUG' if is_development else 'INFO'

        # Eliminar FileHandlers en producción
        if not is_development:
            file_handlers = [handler for handler in config['handlers'] if 'FileHandler' in config['handlers'][handler]['class']]
            for handler in file_handlers:
                del config['handlers'][handler]

        return config

    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        Carga la configuración desde el archivo JSON y ajusta según el entorno.

        Returns:
            Optional[Dict[str, Any]]: Configuración ajustada o None si hay error.
        """
        try:
            # Primero intentar cargar desde LOG_CFG si está definido.
            config_path = os.getenv('LOG_CFG', str(self.config_path))
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return self._adjust_log_level(config)
        except FileNotFoundError as e:
            logging.error(f"Archivo de configuración no encontrado: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar JSON: {e}")
        except PermissionError as e:
            logging.error(f"No se tiene permiso para acceder al archivo: {e}")
        except Exception as e:  # Para casos realmente inesperados.
            logging.error(f"Error inesperado al cargar la configuración: {e}")
        return None


class LoggerConfigurator:
    """Clase singleton para configurar el logger usando una estrategia y filtros dinámicos."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_strategy: Optional[ConfigStrategy] = None, 
                 default_level: int = logging.INFO):
        """
        Inicializa el configurador del logger (solo una vez).

        Args:
            config_strategy (Optional[ConfigStrategy]): Estrategia de configuración.
            default_level (int): Nivel de log por defecto.
        """
        if not self._initialized:
            self.config_strategy = config_strategy or JSONConfigStrategy()
            self.default_level = default_level
            self.filters = {}
            self._logger = None
            self._initialized = True
    
    def register_filter(self, name: str, filter_class: type) -> None:
        """
        Registra un filtro dinámicamente.

        Args:
            name (str): Nombre del filtro.
            filter_class (type): Clase del filtro que hereda de logging.Filter.
        """
        if name not in self.filters:
            self.filters[name] = filter_class()
    
    def configure(self) -> logging.Logger:
        """
        Configura y retorna el logger. Si ya está configurado, retorna la instancia existente.

        Returns:
            logging.Logger: Logger configurado.
        """
        if self._logger is not None:
            return self._logger
            
        config = self.config_strategy.load_config()
        
        if config:
            # Registrar filtros dinámicos.
            if 'filters' not in config:
                config['filters'] = {}
                
            for name, filter_instance in self.filters.items():
                config['filters'][name] = {
                    '()': f"{filter_instance.__class__.__module__}.{filter_instance.__class__.__name__}"
                }
            
            try:
                logging.config.dictConfig(config)
                self._logger = logging.getLogger("app_logger")
            except ValueError as e:  # Error típico en dictConfig.
                logging.error(f"Error en la configuración del logger (dictConfig): {e}")
                self._use_default_config()
            except Exception as e:  # Para errores inesperados.
                logging.error(f"Error inesperado al aplicar la configuración: {e}")
                self._use_default_config()
        else:
            self._use_default_config()
            
        return self._logger
    
    def _use_default_config(self) -> None:
        """Aplica la configuración por defecto cuando falla la configuración principal."""
        logging.basicConfig(
            level=self.default_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self._logger = logging.getLogger("app_logger")
        logging.warning("Usando configuración por defecto del logger.")
