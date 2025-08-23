import shutil
import logging
import pytest
from unittest.mock import patch
from file_processing.file import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

values = [
    ('MemoryOutStream.cpp', 'ascii', 218, 2, 0, 0),
    ('XmlTestReporter.cpp', 'ascii', 130, 3, 0, 1),
    ('arithm.cpp', 'ascii', 2411, 39, 0, 37),
    ('lr.cpp', 'ascii', 604, 6, 11, 44),
    ('scan_9.cc', 'ascii', 544, 3, 1, 51),
    ('bert_defs.cc', 'ascii', 1860, 17, 0, 114),
    ('learner.cc', 'ascii', 1516, 27, 8, 164),
    ('loop.cc', 'ascii', 277, 4, 0, 45),
]

@pytest.mark.parametrize(
    "file_name, encoding, num_lines, num_functions, num_classes, num_comments",
    values
)
def test_cpp_metadata_extraction(file_name, encoding, num_lines, num_functions, num_classes, num_comments, caplog):
    caplog.set_level(logging.DEBUG)
    cpp_file_path = test_files_path / file_name
    cpp_file = File(str(cpp_file_path))

    assert cpp_file.processor.metadata['encoding'] == encoding
    assert cpp_file.processor.metadata['num_lines'] == num_lines
    assert cpp_file.processor.metadata['num_functions'] == num_functions
    assert cpp_file.processor.metadata['num_classes'] == num_classes
    assert cpp_file.processor.metadata['num_comments'] == num_comments

    assert f"Starting processing of C++ file '{cpp_file.path}'." in caplog.text
    assert f"Successfully processed C++ file '{cpp_file.path}'." in caplog.text


@pytest.mark.parametrize("file_name", [name for name, *_ in values])
def test_cpp_invalid_save_location(file_name, caplog):
    caplog.set_level(logging.DEBUG)
    cpp_file = File(str(test_files_path / file_name))
    invalid_save_path = '/non_existent_folder/' + file_name
    with pytest.raises(FileProcessingFailedError):
        cpp_file.save(invalid_save_path)
    assert any(record.levelname == "ERROR" and "Failed to save C++ file" in record.message for record in caplog.records)


@pytest.mark.parametrize("file_name", [name for name, *_ in values])
def test_cpp_processor_open_file_false(file_name, caplog):
    caplog.set_level(logging.DEBUG)
    cpp_file_path = test_files_path / file_name
    with patch("builtins.open") as mock_open:
        file_obj = File(str(cpp_file_path), open_file=False)
        mock_open.assert_not_called()
        assert f"C++ file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_cpp_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    src_path = test_files_path / file_name
    file_obj = File(str(src_path), open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / file_name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied_file = File(str(dest_path))

    assert copied_file.processor.compute_hash(algorithm) == original_hash

    # ✅ Check logging from File.copy()
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text

    # ✅ Check logging from CppFileProcessor
    assert f"Starting processing of C++ file '{copied_file.path}'." in caplog.text
    assert f"Successfully processed C++ file '{copied_file.path}'." in caplog.text


@pytest.mark.parametrize("file_name", [v[0] for v in values])
def test_cpp_copy_integrity_failure(file_name, tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(str(test_files_path / file_name), open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    dest_path = tmp_path / file_name

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(dest_path), verify_integrity=True)

    # ✅ Assert exception message
    assert "Integrity check failed" in str(excinfo.value)

    # ✅ Assert specific error log line
    assert any(
        record.levelname == "ERROR" and "Integrity check failed" in record.message
        for record in caplog.records
    )

    # ✅ Assert that the copy operation was logged
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
