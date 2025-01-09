"""
src/logs/base_filter.py
Base filter module for shared filter functionality.
"""

import logging

class BaseLogFilter(logging.Filter):
    """Base class for log filters with shared functionality."""
    def filter(self, record: logging.LogRecord) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")
