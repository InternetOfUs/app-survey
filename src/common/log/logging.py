from __future__ import absolute_import, annotations

import os


log_level = os.getenv("LOG_LEVEL", "INFO")
log_level_libraries = os.getenv("LOG_LEVEL_LIBS", "DEBUG")

log_handlers = ["console"]
if "LOG_TO_FILE" in os.environ:
    log_handlers.append("file")


def get_logging_configuration(service_name: str):
    """
    Get the logging configuration to be associated to a particular service.

    :param service_name: The name of the service (e.g. ws, backend, rule-engine, ..)
    :return: The logging configuration
    """
    file_name = f"{service_name}.log"

    log_config = {
        "version": 1,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": ""
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "simple",
                "filename": os.path.join(os.getenv("LOGS_DIR", ""), file_name),
                "maxBytes": 10485760,
                "backupCount": 3
            }
        },
        "root": {
            "level": log_level,
            "handlers": log_handlers,
        },
        "loggers": {
            "werkzeug": {
                "level": log_level_libraries,
                "handlers": log_handlers,
                "propagate": 0
            },
            "uhopper": {
                "level": log_level,
                "handlers": log_handlers,
                "propagate": 0
            }
        }
    }

    return log_config
