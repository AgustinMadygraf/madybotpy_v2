"""
Path: core/logs/info_error_filter.py
Filter module for allowing only INFO and ERROR logs.
"""

import logging

class InfoErrorFilter(logging.Filter):
    """Permite solo registros con nivel INFO o ERROR."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno in (logging.INFO, logging.ERROR)
