import shutil
import logging
import pytest
from unittest.mock import patch
from file_processing.file import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

values = [
    ('internal.h', 'ascii', 202, 5, 6, 4, 0, 23),
    ('rtp_av1.h', 'ascii', 132, 2, 19, 0, 0, 13),
    ('wglew.h', 'ascii', 958, 1, 356, 2, 0, 77),
    ('wglext.h', 'ascii', 696, 1, 235, 1, 0, 27),
]

@pytest.mark.parametrize(
    "file_name, encoding, num_lines, num_includes, num_macros, num_structs, num_classes, num_comments",
    values
)
def test_h_metadata_extraction(file_name, encoding, num_lines, num_includes,
                               num_macros, num_structs, num_classes, num_comments, caplog):
    caplog.set_level(logging.DEBUG)
    h_file_path = test_files_path / file_name
    h_file = File(str(h_file_path))

    assert f"Starting processing of H file '{h_file.path}'." in caplog.text
    assert f"Successfully processed H file '{h_file.path}'." in caplog.text

    metadata = h_file.processor.metadata
    assert metadata['encoding'] == encoding
    assert metadata['num_lines'] == num_lines
    assert metadata['num_includes'] == num_includes
    assert metadata['num_macros'] == num_macros
    assert metadata['num_structs'] == num_structs
    assert metadata['num_classes'] == num_classes
    assert metadata['num_comments'] == num_comments

@pytest.mark.parametrize("file_name", [entry[0] for entry in values])
def test_h_invalid_save_location(file_name, caplog):
    caplog.set_level(logging.DEBUG)
    h_file_path = test_files_path / file_name
    h_file = File(str(h_file_path))
    invalid_save_path = '/non_existent_folder/' + file_name
    with pytest.raises(FileProcessingFailedError):
        h_file.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save H file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("file_name", [entry[0] for entry in values])
def test_h_processor_open_file_false(file_name, caplog):
    caplog.set_level(logging.DEBUG)
    h_file_path = test_files_path / file_name
    with patch("builtins.open") as mock_open:
        file_obj = File(str(h_file_path), open_file=False)
        mock_open.assert_not_called()
        assert f"H file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_h_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    path = test_files_path / file_name
    file_obj = File(str(path), open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / file_name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied = File(str(dest_path))
    assert copied.processor.compute_hash(algorithm) == original_hash

    # ✅ Check copy logging from File.copy()
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
def test_h_copy_integrity_failure(file_name, tmp_path, monkeypatch):
    path = test_files_path / file_name
    file_obj = File(str(path), open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / file_name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)