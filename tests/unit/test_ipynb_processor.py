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

variable_names = "path, text_length, num_cells, num_code_cells, num_markdown_cells"
values = [
    (test_files_path / 'convolutional_network_raw.ipynb', 5455, 7, 5, 2),
    (test_files_path / 'neural_network.ipynb', 4517, 11, 9, 2)
]

@pytest.mark.parametrize(variable_names, values)
def test_ipynb_metadata(path, text_length, num_cells, num_code_cells, num_markdown_cells, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    file_obj.process()

    assert f"Starting processing of IPYNB file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed IPYNB file '{file_obj.path}'." in caplog.text

    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_cells'] == num_cells
    assert file_obj.metadata['num_code_cells'] == num_code_cells
    assert file_obj.metadata['num_markdown_cells'] == num_markdown_cells

@pytest.mark.parametrize(variable_names, values)
def test_save_ipynb_metadata(copy_file, text_length, num_cells, num_code_cells, num_markdown_cells, caplog):
    caplog.set_level(logging.DEBUG)
    test_ipynb_metadata(copy_file, text_length, num_cells, num_code_cells, num_markdown_cells, caplog)

@pytest.mark.parametrize("valid_path", [v[0] for v in values])
def test_ipynb_invalid_save_location(valid_path, caplog):
    caplog.set_level(logging.DEBUG)
    ipynb_file = File(valid_path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(valid_path)
    with pytest.raises(FileProcessingFailedError):
        ipynb_file.processor.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save IPYNB file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"IPYNB file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_ipynb_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_ipynb_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / Path(path).name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)