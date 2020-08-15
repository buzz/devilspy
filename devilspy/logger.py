"""devilspy logger."""

import logging
from devilspy.meta import PROGRAM_NAME

logging.basicConfig(format="%(name)s:%(levelname)s: %(message)s")
main_logger = logging.getLogger(PROGRAM_NAME)
main_logger.setLevel(logging.INFO)
