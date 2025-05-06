import logging
from pathlib import Path

LOG_FILE = Path("app") / "app.log"

def setup_logging(level = logging.INFO):
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=level,
        format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(name)s - %(message)s",
        force=True
    )

