import logging
from logging.config import dictConfig
from pathlib import Path

LOG_FILE = Path("app") / "app.log"

def setup_logging(level: int = logging.INFO):
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "detailed",
                "filename": str(LOG_FILE),
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "urllib3":  {"level": "WARNING", "handlers": [], "propagate": False},
            "httpcore": {"level": "WARNING", "handlers": [], "propagate": False},
            "chromadb": {"level": "WARNING", "handlers": [], "propagate": False},
            "chromadb.api.segment": {"level": "WARNING", "handlers": [], "propagate": False},
        },
        "root": {
            "level": level,
            "handlers": ["file"],
        },
    }

    dictConfig(LOGGING_CONFIG)


# def setup_logging(level = logging.INFO):
#     logger = logging.getLogger(__name__)
#     logging.basicConfig(
#         filename=str(LOG_FILE),
#         level=level,
#         format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(name)s - %(message)s",
#         force=True
#     )

#     # Silence other default loggers

#     # Silence Chroma’s telemetry banner
#     logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.WARNING)

#     # Silence httpx request/response logs (used by Chroma under the hood)
#     logging.getLogger("httpx").setLevel(logging.WARNING)

#     logging.getLogger("_trace.py").setLevel(logging.WARNING)

#     logging.getLogger("config.py").setLevel(logging.WARNING)

