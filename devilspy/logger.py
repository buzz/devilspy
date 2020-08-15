"""devilspy logger."""

import logging
from devilspy.meta import PROGRAM_NAME

logging.basicConfig(format="%(levelname)s: %(message)s")
logger = logging.getLogger(PROGRAM_NAME)
logger.setLevel(logging.INFO)
