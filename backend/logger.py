import logging
import os
import sys

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

if os.getenv("DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.debug(" ******** Running in DEBUG Mode. ******** ")
