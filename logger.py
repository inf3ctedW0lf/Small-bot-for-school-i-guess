# logger.py

from __future__ import annotations

import logging
import traceback
from pathlib import Path
from logging.handlers import RotatingFileHandler

import config

# ==========================================================
# LOGGER FACTORY
# ==========================================================

_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger.

    Example:
        logger = get_logger("Portal")
        logger.info("Driver started")
    """

    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    # ------------------------------------------------------
    # Console output
    # ------------------------------------------------------

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    # ------------------------------------------------------
    # Log file
    # ------------------------------------------------------

    logfile = RotatingFileHandler(
        Path(config.MAIN_LOG),
        maxBytes=5 * 1024 * 1024,   # 5 MB
        backupCount=5,
        encoding="utf-8",
    )

    logfile.setLevel(logging.DEBUG)
    logfile.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(logfile)

    _LOGGERS[name] = logger

    return logger


# ==========================================================
# EXCEPTION HELPER
# ==========================================================

def log_exception(logger: logging.Logger, message: str):
    """
    Logs the current exception with traceback.

    Example:

    try:
        ...
    except Exception:
        log_exception(logger, "Failed to scrape portal")
    """

    logger.error(
        "%s\n%s",
        message,
        traceback.format_exc(),
    )


# ==========================================================
# STARTUP BANNER
# ==========================================================

def startup(logger: logging.Logger):
    logger.info("=" * 60)
    logger.info("School Bot starting...")
    logger.info("=" * 60)


def shutdown(logger: logging.Logger):
    logger.info("=" * 60)
    logger.info("School Bot shutting down...")
    logger.info("=" * 60)