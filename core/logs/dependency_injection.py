"""
Path: core/logs/dependency_injection.py
Contenedor de dependencias para inyección de dependencias.
"""

from core.logs.config_logger import LoggerConfigurator

# Crear una instancia global de LoggerConfigurator
configurator = LoggerConfigurator()

# Registrar filtros dinámicos
configurator.register_filter('info_error_filter', lambda: __import__('core.logs.info_error_filter').logs.info_error_filter.InfoErrorFilter())
configurator.register_filter('exclude_http_logs_filter', lambda: __import__('core.logs.exclude_http_logs_filter').logs.exclude_http_logs_filter.ExcludeHTTPLogsFilter())

# Configurar el logger con los filtros registrados
app_logger = configurator.configure()

def get_logger():
    """
    Retorna la instancia global del logger configurado.
    """
    return app_logger
