"""
Logging configuration for the Mafia Online client.

Initializes and configures the global logger used throughout the
Mafia Online client library. The logger outputs messages to stdout
using a standard timestamped format.

Typical usage example:

    from zafiaonline.logger import logger

    logger.info("Application started")
    logger.error("An error occurred")
"""
import logging
import sys

logger = logging.getLogger("zafiaonline")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
