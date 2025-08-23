import os
import shutil
import logging
import pytest
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, text_length, num_lines, num_words"
values = [
    (test_files_path / 'government_of_canada_wikipedia.txt', 38983, 306, 5691),
    (test_files_path / 'usa_government_wikipedia.txt', 47819, 383, 7160)
]


@pytest.mark.parametrize(variable_names, values)
def test_txt_metadata(path, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_lines'] == num_lines
    assert file_obj.metadata['num_words'] == num_words
    assert f"Starting processing of text file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed text file '{file_obj.path}'." in caplog.text


@pytest.mark.parametrize(variable_names, values)
def test_not_opening_file(path, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path, open_file=False)
    assert f"Text file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


@pytest.mark.parametrize(variable_names, values)
def test_save_txt_metadata(copy_file, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(copy_file)
    save_path = copy_file
    file_obj.save(save_path)
    assert f"Saving text file '{file_obj.path}' to '{save_path}'." in caplog.text
    assert f"Text file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_txt_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    txt_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        txt_file.save(invalid_save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save text file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_txt_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_txt_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, "w") as f:
            f.write("corrupted content")

    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / os.path.basename(path), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)