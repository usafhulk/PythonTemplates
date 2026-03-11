"""
logger.py
=========
Configurable structured logging for Wingbrace projects.

Provides a single ``get_logger()`` factory that returns a standard Python
``logging.Logger`` with sensible defaults and optional file output.

Usage::

    from wingbrace.utilities import get_logger

    log = get_logger("my_module")
    log.info("Processing started")
    log.warning("File not found: %s", path)

    # With file output:
    log = get_logger("my_module", log_file="logs/app.log", level="DEBUG")
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


_DEFAULT_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Registry to avoid adding duplicate handlers to the same logger name
_configured: set[str] = set()


def get_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    fmt: str = _DEFAULT_FORMAT,
    datefmt: str = _DATE_FORMAT,
) -> logging.Logger:
    """
    Return a configured ``logging.Logger`` instance.

    Parameters
    ----------
    name:
        Logger name, typically ``__name__`` or the class name.
    level:
        Log level string: ``"DEBUG"``, ``"INFO"``, ``"WARNING"``,
        ``"ERROR"``, or ``"CRITICAL"``.
    log_file:
        Optional path to a rotating log file.  Parent directories are
        created automatically.
    max_bytes:
        Maximum size of the log file before rotation (bytes).
    backup_count:
        Number of rotated backup files to retain.
    fmt:
        Log message format string.
    datefmt:
        Date/time format string.

    Returns
    -------
    logging.Logger
        A configured logger.  Subsequent calls with the same *name* return
        the same logger instance without adding duplicate handlers.
    """
    logger = logging.getLogger(name)

    # Only configure once per logger name
    if name in _configured:
        return logger

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler (rotating)
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    _configured.add(name)
    return logger


def configure_root_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    fmt: str = _DEFAULT_FORMAT,
    datefmt: str = _DATE_FORMAT,
) -> logging.Logger:
    """
    Configure the root logger for the entire application.

    Call this once at application startup.  Individual module loggers
    obtained via ``get_logger()`` will inherit this configuration.

    Parameters
    ----------
    level:
        Root log level.
    log_file:
        Optional rotating log file path.

    Returns
    -------
    logging.Logger
        The root logger.
    """
    return get_logger(
        "root",
        level=level,
        log_file=log_file,
        fmt=fmt,
        datefmt=datefmt,
    )
