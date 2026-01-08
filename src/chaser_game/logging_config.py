"""Logging configuration module for pyglet-readme.

Provides centralized logging setup with support for:
- Multiple log levels (TRACE, DEBUG, INFO, WARNING, ERROR)
- Console and optional file output
- Structured formatting
- Module-specific loggers
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

# Define TRACE level (between DEBUG and NOTSET)
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


class LogConfig:
    """Centralized logging configuration."""

    # Log format for console output
    CONSOLE_FORMAT = "%(levelname)-8s | %(name)s | %(message)s"

    # Log format for file output (includes timestamp)
    FILE_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    # Default log level
    DEFAULT_LEVEL = logging.WARNING

    def __init__(self) -> None:
        """Initialize logging configuration."""
        self._loggers: dict[str, logging.Logger] = {}
        self._file_handler: Optional[logging.FileHandler] = None

    def setup(
        self,
        level: int = DEFAULT_LEVEL,
        log_file: Optional[Path] = None,
    ) -> None:
        """Configure logging system.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR).
            log_file: Optional path to log file. If provided, logs will be written there.
        """
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Remove existing handlers to avoid duplicates
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(self.CONSOLE_FORMAT)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # File handler (if requested)
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            self._file_handler = logging.FileHandler(log_file)
            self._file_handler.setLevel(level)
            file_formatter = logging.Formatter(self.FILE_FORMAT)
            self._file_handler.setFormatter(file_formatter)
            root_logger.addHandler(self._file_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger for a module.

        Args:
            name: Logger name (typically __name__).

        Returns:
            Configured logger instance.
        """
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]

    def close(self) -> None:
        """Close file handlers and cleanup."""
        if self._file_handler:
            self._file_handler.close()


# Global logging configuration instance
_log_config: Optional[LogConfig] = None


def init_logging(
    level: int = LogConfig.DEFAULT_LEVEL,
    log_file: Optional[Path] = None,
) -> None:
    """Initialize the global logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional path to log file.
    """
    global _log_config
    _log_config = LogConfig()
    _log_config.setup(level=level, log_file=log_file)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger instance.
    """
    global _log_config
    if _log_config is None:
        init_logging()
        assert _log_config is not None  # Type guard
    return _log_config.get_logger(name)


def close_logging() -> None:
    """Close logging and cleanup resources."""
    global _log_config
    if _log_config:
        _log_config.close()
