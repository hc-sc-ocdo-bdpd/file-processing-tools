import os
import shutil
from pathlib import Path
from unittest.mock import patch
import pytest
import logging
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, text_length, num_lines, num_words"
values = [
    (test_files_path / 'Python.gitignore', 3139, 163, 403),
    (test_files_path / 'tensorflow.gitignore', 939, 53, 52)
]

@pytest.mark.parametrize(variable_names, values)
def test_gitignore_metadata(path, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_lines'] == num_lines
    assert file_obj.metadata['num_words'] == num_words

    assert f"Starting processing of Gitignore file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed Gitignore file '{file_obj.path}'." in caplog.text
    assert any("Detected encoding" in record.message for record in caplog.records)


@pytest.mark.parametrize(variable_names, values)
def test_not_opening_file(path, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"Gitignore file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


@pytest.mark.parametrize(variable_names, values)
def test_save_gitignore_metadata(copy_file, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    test_gitignore_metadata(copy_file, text_length, num_lines, num_words, caplog)

    file_obj = File(copy_file)
    save_path = copy_file
    file_obj.save(str(save_path))

    assert f"Saving Gitignore file '{file_obj.path}' to '{save_path}'." in caplog.text
    assert f"Gitignore file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_gitignore_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    gitignore_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        gitignore_file.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save Gitignore file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("path", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_gitignore_copy_with_integrity(path, algorithm, tmp_path):
    file_obj = File(path, open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(path).name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied = File(str(dest_path))
    assert copied.processor.compute_hash(algorithm) == original_hash


@pytest.mark.parametrize("path", [v[0] for v in values])
def test_gitignore_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / Path(path).name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)