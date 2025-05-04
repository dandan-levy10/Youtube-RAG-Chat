import logging
from app.services.transcription import get_transcript
from app.core.logging_setup import setup_logging


setup_logging()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    get_transcript("https://www.youtube.com/watch?v=ZrK3L0IXb9c&ab_channel=TechWithTim")