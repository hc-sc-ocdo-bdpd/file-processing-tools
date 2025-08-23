import os
import shutil
import logging
from pathlib import Path
from unittest.mock import patch
import pytest
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, original_format, mode, width, height"
values = [
   (test_files_path / 'HealthCanada.jpeg', 'JPEG', 'RGB', 474, 262),
   (test_files_path / 'MapCanada.jpg', 'JPEG', 'RGB', 4489, 2896)
]

@pytest.mark.parametrize(variable_names, values)
def test_jpeg_metadata(path, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert file_obj.metadata['original_format'] == original_format
    assert file_obj.metadata['mode'] == mode
    assert file_obj.metadata['width'] == width
    assert file_obj.metadata['height'] == height

    assert f"Starting processing of JPEG file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed JPEG file '{file_obj.path}'." in caplog.text

@pytest.mark.parametrize(variable_names, values)
def test_save_jpeg_metadata(copy_file, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)

    # Trigger processing
    file_obj = File(copy_file)

    # Assert metadata values (like test_jpeg_metadata does)
    assert file_obj.metadata['original_format'] == original_format
    assert file_obj.metadata['mode'] == mode
    assert file_obj.metadata['width'] == width
    assert file_obj.metadata['height'] == height

    # Now trigger save and assert logging
    file_obj.save()
    save_path = copy_file

    assert f"Saving JPEG file '{file_obj.path}' to '{save_path}'." in caplog.text
    assert f"JPEG file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_jpeg_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    jpeg_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        jpeg_file.processor.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save JPEG file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()

    assert f"JPEG file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_jpeg_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    path = test_files_path / file_name
    file_obj = File(str(path), open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(file_name).name  # ✅ use just the name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied = File(str(dest_path))
    assert copied.processor.compute_hash(algorithm) == original_hash

    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_jpeg_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / Path(path).name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)