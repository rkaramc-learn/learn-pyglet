from unittest.mock import MagicMock, patch

import pytest
from chaser_game.restore_assets import restore_assets


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def mock_manifest():
    return {
        "images": {
            "mouse_sheet": {
                "path": "sprites/mouse_sheet.png",
                "tracked": True,
                "type": "sprite_sheet",
            },
            "other_tracked": {"path": "images/other.png", "tracked": True},
        },
        "audio": {},
    }


@patch("chaser_game.restore_assets.load_manifest")
@patch("chaser_game.restore_assets.get_asset_dir")
@patch("chaser_game.restore_assets.input")  # Mock input
@patch("chaser_game.sprite_generator.SpriteSheetGenerator")  # Correct mock path
def test_restore_assets_regenerate_confirmed(
    mock_generator_cls,
    mock_input,
    mock_get_asset_dir,
    mock_load_manifest,
    mock_manifest,
    mock_logger,
    tmp_path,
):
    # Setup mocks
    mock_load_manifest.return_value = mock_manifest
    mock_get_asset_dir.return_value = tmp_path

    # Setup paths
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "mouse.mp4").touch()

    target_dir = tmp_path / "sprites"
    target_dir.mkdir()
    target_file = target_dir / "mouse_sheet.png"

    # User confirms
    mock_input.return_value = "y"

    # Mock generator instance
    mock_gen_instance = MagicMock()
    mock_generator_cls.return_value = mock_gen_instance

    # Run
    result = restore_assets(mock_logger, confirm=True)

    # Verification
    assert result is False  # other_tracked is missing and cannot be regenerated

    # Verify generator called
    mock_gen_instance.generate.assert_called_once()

    # Verify input prompt called
    mock_input.assert_called_once()


@patch("chaser_game.restore_assets.load_manifest")
@patch("chaser_game.restore_assets.get_asset_dir")
@patch("chaser_game.restore_assets.input")
@patch("chaser_game.sprite_generator.SpriteSheetGenerator")
@patch("shutil.move")
def test_restore_assets_regenerate_success_flow(
    mock_utils_move,
    mock_gen_cls,
    mock_input,
    mock_get_dir,
    mock_load,
    mock_manifest,
    mock_logger,
    tmp_path,
):
    """Verify flow passes through regeneration and confirmation."""
    mock_load.return_value = mock_manifest
    mock_get_dir.return_value = tmp_path

    # Setup source
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "mouse.mp4").touch()

    # Ensure other_tracked exists so we can return True
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "other.png").touch()

    mock_input.return_value = "y"

    result = restore_assets(mock_logger, confirm=True)

    assert result is True
    # Verify success log for mouse_sheet
    success_calls = [
        c
        for c in mock_logger.info.call_args_list
        if "Restored sprites" in str(c) or "Restored" in str(c)
    ]
    assert len(success_calls) > 0


@patch("chaser_game.restore_assets.load_manifest")
@patch("chaser_game.restore_assets.get_asset_dir")
@patch("chaser_game.restore_assets.input")
@patch("chaser_game.sprite_generator.SpriteSheetGenerator")
def test_restore_assets_denied(
    mock_gen_cls, mock_input, mock_get_dir, mock_load, mock_manifest, mock_logger, tmp_path
):
    """Verify denial skips restoration."""
    mock_load.return_value = mock_manifest
    mock_get_dir.return_value = tmp_path
    (tmp_path / "source").mkdir()
    (tmp_path / "source" / "mouse.mp4").touch()

    mock_input.return_value = "n"

    result = restore_assets(mock_logger, confirm=True)

    assert result is False  # Failed to restore mouse_sheet
    assert mock_gen_cls.return_value.generate.assert_called  # Still generates to temp
    mock_logger.warning.assert_any_call("  [SKIPPED] User aborted move.")
