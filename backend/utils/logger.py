"""Structured JSON logging configuration."""

import logging
import sys
from pythonjsonlogger import jsonlogger


_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
_initialized = False


class _Formatter(jsonlogger.JsonFormatter):
    """JSON formatter with default fields."""

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)
        log_record.setdefault("timestamp", self.formatTime(record))


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with structured JSON output."""
    global _initialized
    if _initialized:
        return

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_Formatter(_LOG_FORMAT))

    root.handlers.clear()
    root.addHandler(handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, initializing logging if needed."""
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)
