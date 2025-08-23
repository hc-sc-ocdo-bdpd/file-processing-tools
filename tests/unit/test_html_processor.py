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

variable_names = "path, text_length, num_lines, num_words"
values = [
    (test_files_path / 'Health - Canada.ca.html', 165405, 3439, 11162)
]

@pytest.mark.parametrize(variable_names, values)
def test_html_metadata(path, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)

    assert f"Starting processing of HTML file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed HTML file '{file_obj.path}'." in caplog.text

    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_lines'] == num_lines
    assert file_obj.metadata['num_words'] == num_words

@pytest.mark.parametrize(variable_names, values)
def test_save_html_metadata(copy_file, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    test_html_metadata(copy_file, text_length, num_lines, num_words, caplog)

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_html_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    html_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        html_file.processor.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save HTML file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"HTML file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_html_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_html_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / Path(path).name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)