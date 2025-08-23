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
    (test_files_path / 'MapleLeaf.heic', 'HEIF', 'RGB', 1600, 1200),
    (test_files_path / 'MapleLeaf.heif', 'HEIF', 'RGB', 1600, 1200)
]

@pytest.mark.parametrize(variable_names, values)
def test_heic_metadata(path, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)

    assert f"Starting processing of HEIC file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed HEIC file '{file_obj.path}'." in caplog.text

    assert file_obj.metadata['original_format'] == original_format
    assert file_obj.metadata['mode'] == mode
    assert file_obj.metadata['width'] == width
    assert file_obj.metadata['height'] == height

@pytest.mark.parametrize(variable_names, values)
def test_save_heic_metadata(copy_file, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)
    test_heic_metadata(copy_file, original_format, mode, width, height, caplog)

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_heic_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    heic_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        heic_file.processor.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save HEIC file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"HEIC file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("path", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_heic_copy_with_integrity(path, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path, open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(path).name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied = File(str(dest_path))
    assert copied.processor.compute_hash(algorithm) == original_hash

    # ✅ Check copy logging from File.copy()
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_heic_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / Path(path).name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)