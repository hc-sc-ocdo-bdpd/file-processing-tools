import os
import shutil
import logging
from unittest.mock import patch
from pathlib import Path
import pytest
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, original_format, mode, width, height"
values = [
    (test_files_path / 'Health_Canada_logo.png', 'GIF', 'P', 303, 40),
    (test_files_path / 'MapCanada.png', 'PNG', 'RGBA', 3000, 2408)
]

@pytest.mark.parametrize(variable_names, values)
def test_png_metadata(path, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert file_obj.metadata['original_format'] == original_format
    assert file_obj.metadata['mode'] == mode
    assert file_obj.metadata['width'] == width
    assert file_obj.metadata['height'] == height
    assert f"Starting processing of PNG file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed PNG file '{file_obj.path}'." in caplog.text

@pytest.mark.parametrize(variable_names, values)
def test_save_png_metadata(copy_file, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)
    test_png_metadata(copy_file, 'PNG', mode, width, height, caplog)
    file_obj = File(copy_file)
    save_path = copy_file
    file_obj.processor.save(save_path)
    assert f"Saving PNG file '{file_obj.path}' to '{save_path}'." in caplog.text
    assert f"PNG file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_png_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    png_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        png_file.processor.save(invalid_save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save PNG file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"PNG file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_png_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_png_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, 'w') as f:
            f.write("corrupted png data")

    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / Path(path).name, verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)