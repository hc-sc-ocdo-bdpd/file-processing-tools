import shutil
import pytest
from unittest.mock import patch
import logging
from file_processing.file import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

values = [
    ('arduino-cli.go', 'ascii', 723, 6, 3, 0),
    ('bernoulli_nb.go', 'ascii', 334, 1, 1, 0),
    ('knn.go', 'ascii', 475, 3, 2, 0),
    ('network.go', 'ascii', 133, 0, 1, 0),
]

@pytest.mark.parametrize(
    "file_name, encoding, num_lines, num_functions, num_structs, num_interfaces",
    values
)
def test_go_metadata_extraction(file_name, encoding, num_lines, num_functions, num_structs, num_interfaces, caplog):
    caplog.set_level(logging.DEBUG)
    go_file_path = test_files_path / file_name
    go_file = File(str(go_file_path))

    assert go_file.processor.metadata['encoding'] == encoding
    assert go_file.processor.metadata['num_lines'] == num_lines
    assert go_file.processor.metadata['num_functions'] == num_functions
    assert go_file.processor.metadata['num_structs'] == num_structs
    assert go_file.processor.metadata['num_interfaces'] == num_interfaces

    assert f"Starting processing of Go file '{go_file.path}'." in caplog.text
    assert f"Successfully processed Go file '{go_file.path}'." in caplog.text
    assert any("Detected encoding" in record.message for record in caplog.records)


@pytest.mark.parametrize("file_name", [name for name, *_ in values])
def test_go_invalid_save_location(file_name, caplog):
    caplog.set_level(logging.DEBUG)
    go_file = File(str(test_files_path / file_name))
    invalid_save_path = '/non_existent_folder/' + file_name
    with pytest.raises(FileProcessingFailedError):
        go_file.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save Go file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("file_name", [name for name, *_ in values])
def test_go_processor_open_file_false(file_name, caplog):
    caplog.set_level(logging.DEBUG)
    go_file_path = test_files_path / file_name
    with patch("builtins.open") as mock_open:
        go_file = File(str(go_file_path), open_file=False)
        mock_open.assert_not_called()
        assert f"Go file '{go_file.path}' was not opened (open_file=False)." in caplog.text


@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_go_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    path = test_files_path / file_name
    file_obj = File(str(path), open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / file_name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied = File(str(dest_path))
    assert copied.processor.compute_hash(algorithm) == original_hash

    # ✅ Check logging
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text


@pytest.mark.parametrize("file_name", [v[0] for v in values])
def test_go_copy_integrity_failure(file_name, tmp_path, monkeypatch):
    path = test_files_path / file_name
    file_obj = File(str(path), open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / file_name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)