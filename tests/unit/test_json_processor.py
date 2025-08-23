import os
import shutil
import logging
import pytest
from unittest.mock import patch
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, num_keys, key_names, empty_values"
values = [
    (test_files_path / 'coffee.json', 15, ['quiz', 'sport', 'q1', 'question', 'options', 'answer', 'maths', 'q1', 'question', 'options', 'answer', 'q2', 'question', 'options', 'answer'], 0),
    (test_files_path / 'sample.json', 9, ['array', 'boolean', 'color', 'null', 'number', 'object', 'a', 'c', 'string'], 1)
]

@pytest.mark.parametrize(variable_names, values)
def test_json_metadata(path, num_keys, key_names, empty_values, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert file_obj.metadata['num_keys'] == num_keys
    assert file_obj.metadata['key_names'] == key_names
    assert file_obj.metadata['empty_values'] == empty_values
    assert f"Starting processing of JSON file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed JSON file '{file_obj.path}'." in caplog.text

@pytest.mark.parametrize(variable_names, values)
def test_save_json_metadata(copy_file, num_keys, key_names, empty_values, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(copy_file)
    file_obj.processor.save()
    save_path = copy_file
    assert f"Saving JSON file '{file_obj.path}' to '{save_path}'." in caplog.text
    assert f"JSON file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text
    test_json_metadata(copy_file, num_keys, key_names, empty_values, caplog)

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_json_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    json_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        json_file.processor.save(invalid_save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save JSON file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_json_open_file_false(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"JSON file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_json_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_json_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt(src, dst, *, follow_symlinks=True):
        with open(dst, 'w') as f:
            f.write("INVALID JSON")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / path.name, verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)