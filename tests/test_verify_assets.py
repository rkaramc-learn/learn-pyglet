import logging
from unittest.mock import MagicMock

import pytest
from chaser_game.restore_assets import (
    calculate_sha256,
    verify_asset_integrity,
    verify_audio_metadata,
    verify_image_metadata,
)


@pytest.fixture
def mock_logger():
    return MagicMock(spec=logging.Logger)


@pytest.fixture
def temp_image_file(tmp_path):
    p = tmp_path / "test.png"
    # Create a small valid PNG
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="red")
    img.save(p)
    return p


@pytest.fixture
def temp_audio_file(tmp_path):
    p = tmp_path / "test.wav"
    import wave

    with wave.open(str(p), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b"\x00" * 44100 * 2)  # 1 sec silence (2 bytes per sample)
    return p


def test_calculate_sha256(tmp_path):
    p = tmp_path / "data.bin"
    p.write_bytes(b"hello world")
    # echo -n "hello world" | sha256sum
    # b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
    expected = "B94D27B9934D3E08A52E52D7DA7DABFAC484EFE37A5380EE9088F7ACE2EFCDE9"
    assert calculate_sha256(p) == expected


def test_verify_image_metadata_success(temp_image_file, mock_logger):
    cfg = {"dimensions": [100, 100], "format": "PNG"}
    assert verify_image_metadata(temp_image_file, cfg, mock_logger)
    mock_logger.error.assert_not_called()


def test_verify_image_metadata_fail_dims(temp_image_file, mock_logger):
    cfg = {"dimensions": [200, 200], "format": "PNG"}
    assert not verify_image_metadata(temp_image_file, cfg, mock_logger)
    mock_logger.error.assert_called()


def test_verify_image_metadata_fail_format(temp_image_file, mock_logger):
    # It is PNG, expect JPEG
    cfg = {"dimensions": [100, 100], "format": "JPEG"}
    assert not verify_image_metadata(temp_image_file, cfg, mock_logger)
    mock_logger.error.assert_called()


def test_verify_audio_metadata_success(temp_audio_file, mock_logger):
    cfg = {"channels": 1, "sample_rate": 44100, "duration_seconds": 1.0}
    assert verify_audio_metadata(temp_audio_file, cfg, mock_logger)
    mock_logger.error.assert_not_called()


def test_verify_audio_metadata_fail(temp_audio_file, mock_logger):
    cfg = {"channels": 2}  # File is mono
    assert not verify_audio_metadata(temp_audio_file, cfg, mock_logger)
    mock_logger.error.assert_called()


def test_verify_asset_integrity_hash_mismatch(temp_image_file, mock_logger):
    # Hash of "hello"
    wrong_hash = "2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824"
    cfg = {"sha256": wrong_hash}
    assert not verify_asset_integrity(temp_image_file, cfg, "sprite", mock_logger)
    mock_logger.error.assert_called_with(f"  [FAIL] Hash mismatch {temp_image_file.name}")


def test_verify_asset_integrity_full_pass(temp_image_file, mock_logger):
    # Calculate real hash
    real_hash = calculate_sha256(temp_image_file)
    cfg = {"sha256": real_hash, "dimensions": [100, 100], "format": "PNG"}
    assert verify_asset_integrity(temp_image_file, cfg, "sprite", mock_logger)
