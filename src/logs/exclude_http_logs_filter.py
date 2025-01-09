"""
src/logs/ExcludeHTTPLogsFilter.py
Filter module for excluding specific HTTP logs.
"""

import logging

class ExcludeHTTPLogsFilter(logging.Filter):
    """Filters out HTTP GET and POST requests from logs."""
    # pylint: disable=too-few-public-methods
    def filter(self, record):
        """Exclude log records containing 'GET /' or 'POST /'."""
        return 'GET /' not in record.getMessage() and 'POST /' not in record.getMessage()
