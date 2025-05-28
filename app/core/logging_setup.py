import logging
from logging import NullHandler
from logging.config import dictConfig
from pathlib import Path
import sys
import httpx


LOG_FILE = Path("app") / "app.log"

class DropHttpxBelowWarning(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # If this is an httpx log AND it's below WARNING, drop it.
        if record.name.startswith("httpx") and record.levelno < logging.WARNING:
            return False
        return True
    
# ✅ More general filter for noisy external libs
class DropNoisyExternalBelowWarning(logging.Filter):
    NOISY_PREFIXES = (
        "httpx", "httpcore", "uvicorn", "watchfiles", "sqlalchemy"
    )

    def filter(self, record: logging.LogRecord) -> bool:
        if any(record.name.startswith(prefix) for prefix in self.NOISY_PREFIXES):
            return record.levelno >= logging.WARNING
        return True  # Allow everything else through
    

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # ✅ Silently drop httpx DEBUG and INFO logs
        if record.name.startswith("httpx") and record.levelno < logging.WARNING:
            return

        # Forward everything else to its original logger
        logging.getLogger(record.name).handle(record)

def configure_logging(level: int = logging.DEBUG):
    # # ✅ Remove existing root handlers
    # root_logger = logging.getLogger()
    # for h in root_logger.handlers[:]:
    #     root_logger.removeHandler(h)

    # # ✅ Attach the InterceptHandler to the root logger
    # root_logger.addHandler(InterceptHandler())
    # root_logger.setLevel(logging.DEBUG)  # Capture everything, filter inside emit()

    
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

# def configure_logging(level: int = logging.DEBUG):
#     dictConfig({
#     "version": 1,
#     "disable_existing_loggers": True,
#     "filters": {
#         "drop_httpx_below_warning": {
#             "()":DropHttpxBelowWarning
#         }
#     },
#     "formatters": {
#         "detailed": {
#             # "format": "%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(name)s - %(message)s",
#             "format": "%(asctime)s %(levelname)-8s [%(name)s | %(filename)s:%(lineno)d] - %(message)s",
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#         # mimic Uvicorn's colored console
#         "uvicorn_console": {
#             "()": "uvicorn.logging.DefaultFormatter",
#             "fmt": "%(levelprefix)s %(message)s",
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#             "use_colors": True,
#         },
#     },
#     "handlers": {
#         "app_file": {
#             "class": "logging.FileHandler",
#             "level": level,           # INFO & WARNING into app.log
#             "formatter": "detailed",
#             "filename": "app/app.log",
#             "encoding": "utf-8",
#             "filters": ["drop_httpx_below_warning"],
#         },
#         "error_file": {
#             "class": "logging.FileHandler",
#             "level": "ERROR",          # ERROR & CRITICAL into error.log
#             "formatter": "detailed",
#             "filename": "app/error.log",
#             "encoding": "utf-8",
#             "filters": ["drop_httpx_below_warning"],
#         },
#         "console": {
#             "class": "logging.StreamHandler",
#             "level": level,           # INFO+ of Uvicorn into console
#             "formatter": "uvicorn_console",
#             "stream": sys.stderr,
#         },
#     },
#     "loggers": {
#         "app": {
#             "level": "INFO",
#             "handlers": ["app_file"],
#             "propagate": True,
#         },
#         "uvicorn.error": {
#             "level": "INFO",
#             "handlers": ["console", "error_file"],
#             "propagate": True,
#         },
#         "uvicorn.access": {
#             "level": "INFO",
#             "handlers": ["console"],
#             "propagate": True,
#         },
#         # silence SQLAlchemy INFO
#         "sqlalchemy.engine.Engine": {
#             "level": "WARNING",
#             "handlers": [],
#             "propagate": False,
#         },
#         # silence httpx INFO
#         "httpx": {
#             "level": "WARNING",
#             "handlers": [],
#             "propagate": False,
#         },
#         # silence httpx INFO
#         "httpx._config": {
#             "level": "WARNING",
#             "handlers": [],
#             "propagate": False,
#         },
#         # silence httpx INFO
#         "httpx._client": {
#             "level": "WARNING",
#             "handlers": [],
#             "propagate": False,
#         },
#         # silence httpx INFO
#         "httpcore": {
#             "level": "WARNING",
#             "handlers": [],
#             "propagate": False,
#         },
#     },
#     "root": {
#         "level": "ERROR",
#         "handlers": ["error_file"],
#     },
# })
#     # ✅ Silencing httpx-style loggers AFTER dictConfig is applied
#     for name in ["httpx", "httpx._client", "httpx._config", "httpcore"]:
#         logger = logging.getLogger(name)
#         logger.setLevel(logging.WARNING)
#         logger.handlers = [NullHandler()]
#         logger.propagate = False

#     logging.getLogger("httpx").disabled = True
#     logging.getLogger("httpx._config").disabled = True
#     logging.getLogger("httpx._client").disabled = True
#     logging.getLogger("httpcore").disabled = True

#     # for name in ("httpx", "httpx._config", "httpx._client", "httpcore"):
#     #     logging.getLogger(name).setLevel(logging.WARNING)
    
#     #     # ——— ABSOLUTELY SILENCE HTTPX DEBUG/INFO ———
#     # for name in ("httpx", "httpx._config", "httpx._client", "httpcore"):
#     #     lg = logging.getLogger(name)
#     #     lg.disabled   = True           # kills the logger outright
#     #     lg.handlers.clear()            # no chance of any handler running
#     #     lg.propagate  = False          # will not bubble up anywhere
    
#     # httpx_logger = logging.getLogger("httpx")
#     # httpx_logger.setLevel(logging.CRITICAL)  # drop DEBUG/INFO/WARNING
#     # httpx_logger.propagate = False           # don’t bubble anywhere
#     # httpx_logger.handlers.clear()            # no handlers to accidentally pick up

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




