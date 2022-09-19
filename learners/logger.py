import logging
import os
import sys


EXERCISE_INFO = """
        Make sure, the file exists and contains the respective information in the following JSON format:
        {
            "c9e632fe3aaac273a0eac6f8963b7b41": {
                "child_weight": 4,
                "exercise_name": "sample exercise",
                "exercise_type": "form",
                "global_exercise_id": "c9e632fe3aaac273a0eac6f8963b7b41",
                "local_exercise_id": 1,
                "order_weight": 7141,
                "page_title": "title of page containing the exercise",
                "parent_page_title": "chapter title",
                "parent_weight": 1,
                "root_weight": 7
            }
        }
        """

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

if os.getenv("DEBUG"):
    logger.setLevel(logging.DEBUG)
    logger.debug(" ******** Running in DEBUG Mode. ******** ")
