import logging
from unittest.mock import MagicMock, patch

import pytest
from chaser_game.cli import cli
from click.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking click commands."""
    return CliRunner()


@patch("chaser_game.cli.init_logging")
@patch("chaser_game.cli.main")
def test_play_defaults(
    mock_main: MagicMock, mock_init_logging: MagicMock, runner: CliRunner
) -> None:
    """Test play command with default arguments."""
    result = runner.invoke(cli, ["play"])

    assert result.exit_code == 0
    # Verify default logging (WARNING)
    mock_init_logging.assert_called_once_with(level=logging.WARNING, log_file=None)
    # Verify main called with default screenshots=False
    mock_main.assert_called_once_with(capture_screenshots=False, show_fps=False)


@patch("chaser_game.cli.init_logging")
@patch("chaser_game.cli.main")
def test_play_verbose_1(
    mock_main: MagicMock, mock_init_logging: MagicMock, runner: CliRunner
) -> None:
    """Test play command with -v (INFO)."""
    result = runner.invoke(cli, ["play", "-v"])

    assert result.exit_code == 0
    mock_init_logging.assert_called_once_with(level=logging.INFO, log_file=None)


@patch("chaser_game.cli.init_logging")
@patch("chaser_game.cli.main")
def test_play_verbose_2(
    mock_main: MagicMock, mock_init_logging: MagicMock, runner: CliRunner
) -> None:
    """Test play command with -vv (DEBUG)."""
    result = runner.invoke(cli, ["play", "-vv"])

    assert result.exit_code == 0
    mock_init_logging.assert_called_once_with(level=logging.DEBUG, log_file=None)


@patch("chaser_game.cli.init_logging")
@patch("chaser_game.cli.main")
def test_play_log_file(
    mock_main: MagicMock, mock_init_logging: MagicMock, runner: CliRunner
) -> None:
    """Test play command with --log-file."""
    from pathlib import Path

    result = runner.invoke(cli, ["play", "--log-file", "test.log"])

    assert result.exit_code == 0
    # Note: Click converts path to Path object
    mock_init_logging.assert_called_once()
    call_args = mock_init_logging.call_args
    assert call_args.kwargs["level"] == logging.WARNING
    assert isinstance(call_args.kwargs["log_file"], Path)
    assert str(call_args.kwargs["log_file"]) == "test.log"


@patch("chaser_game.cli.init_logging")
@patch("chaser_game.cli.main")
def test_play_screenshots_enabled(
    mock_main: MagicMock, mock_init_logging: MagicMock, runner: CliRunner
) -> None:
    """Test play command with --screenshots."""
    result = runner.invoke(cli, ["play", "--screenshots"])

    assert result.exit_code == 0
    mock_main.assert_called_once_with(capture_screenshots=True, show_fps=False)


@patch("chaser_game.cli.init_logging")
@patch("chaser_game.cli.main")
def test_play_screenshots_disabled_explicitly(
    mock_main: MagicMock, mock_init_logging: MagicMock, runner: CliRunner
) -> None:
    """Test play command with --no-screenshots."""
    result = runner.invoke(cli, ["play", "--no-screenshots"])

    assert result.exit_code == 0
    mock_main.assert_called_once_with(capture_screenshots=False, show_fps=False)
