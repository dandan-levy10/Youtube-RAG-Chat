import logging
import sys
from logging.config import dictConfig
from pathlib import Path

LOG_FILE = Path("app") / "app.log"
    

def configure_logging(level: int = logging.DEBUG):
    
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,          
        "filters": {
            "noisy_below_warning": {
                "()": DropNoisyExternalBelowWarning        
            }
        },
        "formatters": {
            "detailed": {
                "format": "%(asctime)s %(levelname)-8s "
                          "[%(filename)s:%(lineno)d] %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "uvicorn_console": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "use_colors": True,
            },
        },

        # 👇 NEW: a do-nothing handler
        "handlers": {
            "null": { "class": "logging.NullHandler" },

            "app_file": {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "detailed",
                "filename": "app/app.log",
                "encoding": "utf-8",
                "filters": ["noisy_below_warning"],
            },
            "error_file": {
                "class": "logging.FileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "app/error.log",
                "encoding": "utf-8",
                "filters": ["noisy_below_warning"],
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "uvicorn_console",
                "stream": sys.stderr,
            },
        },

        # 👇 Wire every noisy transport logger to the `null` handler
        "loggers": {
            # --- YOUR CODE BASE ------------------------------------------
            "app":            { "level": "DEBUG", "handlers": [], "propagate": True },
            # "error.log":      {"level": "ERROR", "handlers": ["error_file"], "propagate": False },
            
            # --- EXTERNAL LIBS YOU STILL WANT IN CONSOLE -----------------
            "uvicorn.error":  { "level": "INFO", "handlers": ["console"], "propagate": False },
            "uvicorn.access": { "level": "INFO", "handlers": ["console"], "propagate": False },
            "uvicorn.access.httptools_impl": { "level": "WARNING", "handlers": ["console"], "propagate": True },
            "sqlalchemy.engine.Engine": { "level": "WARNING", "handlers": [], "propagate": True },
            
            #  Watchfiles spam" don't attach handlers, let root+filter decide
            "watchfiles.main": { "level": "WARNING", "handlers": [], "propagate": True },
            

            # silence httpx & transport stack completely
            "httpx":          { "level": "WARNING", "handlers": ["null"], "propagate": False },
            "httpx._client":  { "level": "WARNING", "handlers": ["null"], "propagate": False },
            "httpx._config":  { "level": "WARNING", "handlers": ["null"], "propagate": False },
            "httpcore":       { "level": "WARNING", "handlers": ["null"], "propagate": False },
        },

        "root": {
            "level": "DEBUG",
            "handlers": ["error_file", "app_file"],
        },
    })

# More general filter for noisy external libs
class DropNoisyExternalBelowWarning(logging.Filter):
    NOISY_PREFIXES = (
        "httpx", "httpcore", "uvicorn", "watchfiles", "sqlalchemy"
    )

    def filter(self, record: logging.LogRecord) -> bool:
        if any(record.name.startswith(prefix) for prefix in self.NOISY_PREFIXES):
            return record.levelno >= logging.WARNING
        return True  # Allow everything else through

def setup_logging(level: int = logging.DEBUG):
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




