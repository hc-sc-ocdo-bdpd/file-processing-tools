import logging
from unittest.mock import patch
import shutil
import pytest
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

# Define test parameters including path and expected metadata values
variable_names = "path, num_lines, num_functions, num_classes, num_imports, num_docstrings, text_length"
values = [
    (test_files_path / 'backend.py', 6503, 224, 5, 69, 194, 205761),
    (test_files_path / 'align.py', 213, 8, 0, 16, 3, 6173)
]

@pytest.mark.parametrize(variable_names, values)
def test_python_metadata(path, num_lines, num_functions, num_classes, num_imports, num_docstrings, text_length, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert file_obj.metadata['num_lines'] == num_lines
    assert file_obj.metadata['num_functions'] == num_functions
    assert file_obj.metadata['num_classes'] == num_classes
    assert len(file_obj.metadata['imports']) == num_imports
    assert len(file_obj.metadata['docstrings']) == num_docstrings
    assert len(file_obj.metadata['text']) == text_length
    assert f"Starting processing of PY file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed PY file '{file_obj.path}'." in caplog.text

@pytest.mark.parametrize(variable_names, values)
def test_not_opening_file(path, num_lines, num_functions, num_classes, num_imports, num_docstrings, text_length, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"PY file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize(variable_names, values)
def test_save_python_metadata(copy_file, num_lines, num_functions, num_classes, num_imports, num_docstrings, text_length, caplog, tmp_path):
    caplog.set_level(logging.DEBUG)
    file_obj = File(copy_file)

    save_path = tmp_path / "saved_backend.py"
    file_obj.save(save_path)

    assert f"Saving PY file '{file_obj.path}' to '{save_path}'." in caplog.text
    assert f"PY file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text


invalid_save_locations_python = [
    (test_files_path / 'backend.py', '/non_existent_folder/backend.py')
]

@pytest.mark.parametrize("path, save_path", invalid_save_locations_python)
def test_py_invalid_save_location(path, save_path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    with pytest.raises(FileProcessingFailedError):
        file_obj.save(save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save PY file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_py_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_py_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, "w") as f:
            f.write("corrupted python script")

    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / Path(path).name, verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)