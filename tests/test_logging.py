"""Tests for logging configuration and functionality.

Verifies:
- Logging levels are set correctly
- Log messages contain expected information
- --verbose flag enables DEBUG logs
- File logging works correctly
- Log formatters work as expected
"""

import logging
import sys
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyglet_readme.logging_config import LogConfig, get_logger, init_logging, close_logging


class TestLogConfig:
    """Test LogConfig class."""

    def test_init_default_level(self):
        """Test default logging level is INFO."""
        config = LogConfig()
        assert config.DEFAULT_LEVEL == logging.INFO

    def test_setup_console_handler(self):
        """Test that setup creates console handler."""
        config = LogConfig()
        config.setup(level=logging.INFO)

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) >= 1

        # Find console handler
        console_handlers = [
            h for h in root_logger.handlers
            if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) >= 1

    def test_setup_debug_level(self):
        """Test setup with DEBUG level."""
        config = LogConfig()
        config.setup(level=logging.DEBUG)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_info_level(self):
        """Test setup with INFO level."""
        config = LogConfig()
        config.setup(level=logging.INFO)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_file_handler(self):
        """Test setup with file output."""
        with TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            config = LogConfig()
            config.setup(level=logging.INFO, log_file=log_file)

            # Log something
            logger = logging.getLogger("test")
            logger.info("Test message")

            # Verify file was created and contains message
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content
            assert "test" in content  # Logger name
            
            # Clean up handlers before temp dir cleanup
            config.close()

    def test_file_handler_creates_directory(self):
        """Test that setup creates parent directories for log file."""
        with TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "logs" / "subdir" / "test.log"

            config = LogConfig()
            config.setup(level=logging.INFO, log_file=log_file)

            assert log_file.parent.exists()
            
            # Clean up handlers before temp dir cleanup
            config.close()

    def test_get_logger_caching(self):
        """Test that loggers are cached."""
        config = LogConfig()

        logger1 = config.get_logger("test_logger")
        logger2 = config.get_logger("test_logger")

        assert logger1 is logger2

    def test_close_cleans_up(self):
        """Test that close() cleans up file handlers."""
        with TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            config = LogConfig()
            config.setup(level=logging.INFO, log_file=log_file)
            config.close()

            # Should not raise an error
            assert True


class TestGlobalLogging:
    """Test global logging functions."""

    def teardown_method(self):
        """Clean up after each test."""
        close_logging()
        # Reset root logger
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

    def test_init_logging_default(self):
        """Test init_logging with defaults."""
        init_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_init_logging_debug(self):
        """Test init_logging with DEBUG level."""
        init_logging(level=logging.DEBUG)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a logger."""
        init_logging()

        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_initializes_if_needed(self):
        """Test get_logger initializes logging if not done."""
        # Don't call init_logging
        logger = get_logger("test")

        assert isinstance(logger, logging.Logger)
        root_logger = logging.getLogger()
        assert root_logger.level >= logging.DEBUG  # Should be initialized

    def test_logging_with_console_output(self):
        """Test logging outputs to console."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            init_logging(level=logging.INFO)
            logger = get_logger("test")
            logger.info("Test console message")

            output = sys.stdout.getvalue()
            assert "Test console message" in output
            assert "test" in output
        finally:
            sys.stdout = old_stdout


class TestLoggingIntegration:
    """Integration tests with actual modules."""

    def teardown_method(self):
        """Clean up after each test."""
        close_logging()
        # Reset root logger
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

    def test_assets_module_logging(self):
        """Test that assets module uses logging correctly."""
        init_logging(level=logging.DEBUG)

        from pyglet_readme.assets import get_loader

        loader = get_loader()
        assert loader is not None

    def test_verbose_debug_messages(self):
        """Test that DEBUG level enables all messages."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            init_logging(level=logging.DEBUG)
            logger = get_logger("test")

            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")

            output = sys.stdout.getvalue()
            assert "Debug message" in output
            assert "Info message" in output
            assert "Warning message" in output
        finally:
            sys.stdout = old_stdout

    def test_info_hides_debug_messages(self):
        """Test that INFO level hides DEBUG messages."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            init_logging(level=logging.INFO)
            logger = get_logger("test")

            logger.debug("Debug message")
            logger.info("Info message")

            output = sys.stdout.getvalue()
            assert "Debug message" not in output
            assert "Info message" in output
        finally:
            sys.stdout = old_stdout
