"""
src/logs/info_error_filter.py
Filter module for allowing only INFO and ERROR logs.
"""

import logging

class InfoErrorFilter(logging.Filter):
    """Filters logs to allow only INFO and ERROR levels."""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        """Allow log records with level INFO or ERROR."""
        return record.levelno in (logging.INFO, logging.ERROR)
