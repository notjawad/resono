import logging
from logging.config import dictConfig


def configure_logger():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "📅 %(asctime)s - 🤖 %(name)s - ⚙️ %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %I:%M %p",  # Use 12-hour format with AM/PM
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "standard",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": "bot.log",
                    "level": "DEBUG",
                    "formatter": "standard",
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "resono_bot": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": True,
                },
            },
        }
    )

    return logging.getLogger("resono_bot")
