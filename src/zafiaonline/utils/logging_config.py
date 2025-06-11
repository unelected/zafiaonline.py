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