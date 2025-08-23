import os
import logging
from pathlib import Path
from unittest.mock import patch
import shutil
import pytest
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

# Data fixture
test_files_path = get_test_files_path()
variable_names = (
    "path, text_length, encoding, num_rows, num_cols, num_cells, empty_cells"
)
values = [
    (test_files_path / '2021_Census_English.csv', 6084302, 'ISO-8859-1', 36835, 23, 847205, 253932),
    (test_files_path / 'Approved_Schools_2023_10_01.csv', 1403268, 'UTF-8-SIG', 5385, 13, 70005, 73)
]

@pytest.mark.parametrize(variable_names, values)
def test_csv_metadata(path, text_length, encoding, num_rows, num_cols, num_cells, empty_cells, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['encoding'] == encoding
    assert file_obj.metadata['num_rows'] == num_rows
    assert file_obj.metadata['num_cols'] == num_cols
    assert file_obj.metadata['num_cells'] == num_cells
    assert file_obj.metadata['empty_cells'] == empty_cells

    assert f"Starting processing of CSV file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed CSV file '{file_obj.path}'." in caplog.text


@pytest.mark.parametrize(variable_names, values)
def test_save_csv_metadata(copy_file, text_length, encoding, num_rows, num_cols, num_cells, empty_cells, caplog):
    caplog.set_level(logging.DEBUG)
    test_csv_metadata(copy_file, text_length, encoding, num_rows, num_cols, num_cells, empty_cells, caplog)


@pytest.mark.parametrize("valid_path", [p for p, *_ in values])
def test_csv_invalid_save_location(valid_path, caplog):
    caplog.set_level(logging.DEBUG)
    csv_file = File(valid_path)
    invalid_path = '/non_existent_folder/' + os.path.basename(str(valid_path))
    with pytest.raises(FileProcessingFailedError):
        csv_file.processor.save(invalid_path)
    assert any(record.levelname == "ERROR" and "Failed to save CSV file" in record.message for record in caplog.records)


@pytest.mark.parametrize(variable_names, values)
def test_not_opening_file(path, text_length, encoding, num_rows, num_cols, num_cells, empty_cells, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"CSV file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


@pytest.mark.parametrize(variable_names, values)
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_csv_copy_with_integrity(path, tmp_path, algorithm,
                                 text_length, encoding, num_rows, num_cols, num_cells, empty_cells, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path, open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest = tmp_path / Path(path).name
    file_obj.copy(str(dest), verify_integrity=True)

    # ✅ Check copy logging from File.copy()
    assert f"Copying file from '{file_obj.file_path}' to '{dest}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest}'." in caplog.text

    saved = File(str(dest))

    # ✅ Check processor metadata
    assert len(saved.metadata['text']) == text_length
    assert saved.metadata['encoding'] == encoding
    assert saved.metadata['num_rows'] == num_rows
    assert saved.metadata['num_cols'] == num_cols
    assert saved.metadata['num_cells'] == num_cells
    assert saved.metadata['empty_cells'] == empty_cells

    # ✅ Check final hash
    assert saved.processor.compute_hash(algorithm) == original_hash

    # ✅ Check processor logging from CsvFileProcessor
    assert f"Starting processing of CSV file '{saved.path}'." in caplog.text
    assert f"Successfully processed CSV file '{saved.path}'." in caplog.text


@pytest.mark.parametrize("path", [p for p, *_ in values])
def test_csv_copy_integrity_failure(path, tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write('CORRUPTED!')
    monkeypatch.setattr(shutil, 'copy2', corrupt)

    dest = tmp_path / Path(path).name

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(dest), verify_integrity=True)

    # ✅ Check raised error
    assert 'Integrity check failed' in str(excinfo.value)

    # ✅ Check logging from File.copy()
    assert f"Copying file from '{file_obj.file_path}' to '{dest}' with integrity verification=True." in caplog.text
    assert any(record.levelname == "ERROR" and "Integrity check failed" in record.message for record in caplog.records)
