import logging
from pathlib import Path
import shutil
import pytest
from file_processing import File
from file_processing.processors.generic_processor import GenericFileProcessor
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

unsupported_files = [
    test_files_path / 'unsupported_file_1.xyz',
    test_files_path / 'unsupported_file_2.abcd'
]

@pytest.mark.parametrize("file_path", unsupported_files)
def test_processor_is_generic(file_path):
    file_obj = File(file_path)
    assert isinstance(file_obj.processor, GenericFileProcessor)

@pytest.mark.parametrize("file_path", unsupported_files)
def test_metadata_has_message(file_path):
    file_obj = File(file_path)
    assert 'message' in file_obj.processor.metadata
    assert file_obj.processor.metadata['message'] == (
        "This is a generic processor. Limited functionality available. File was not opened"
    )

@pytest.mark.parametrize("file_path", unsupported_files)
def test_file_attributes(file_path):
    file_obj = File(file_path)
    processor = file_obj.processor

    assert processor.file_path == Path(file_path)
    assert processor.file_name == Path(file_path).name
    assert processor.extension == Path(file_path).suffix
    assert processor.size == Path(file_path).stat().st_size
    assert processor.modification_time == Path(file_path).stat().st_mtime
    assert processor.access_time == Path(file_path).stat().st_atime
    assert processor.creation_time == Path(file_path).stat().st_ctime
    assert processor.parent_directory == Path(file_path).parent
    assert processor.is_file == Path(file_path).is_file()
    assert processor.is_symlink == Path(file_path).is_symlink()
    assert processor.absolute_path == Path(file_path).resolve()

@pytest.mark.parametrize("file_path", unsupported_files)
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_generic_copy_with_integrity(file_path, algorithm, tmp_path):
    file_obj = File(file_path, open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(file_path).name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied = File(str(dest_path))
    assert copied.processor.compute_hash(algorithm) == original_hash
    assert copied.metadata == file_obj.metadata

@pytest.mark.parametrize("file_path", unsupported_files)
def test_generic_copy_integrity_failure(file_path, tmp_path, monkeypatch):
    file_obj = File(file_path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(tmp_path / Path(file_path).name), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)

@pytest.mark.parametrize("file_path", unsupported_files)
def test_generic_process_logs(file_path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(file_path)
    file_obj.processor.process()
    assert f"Processing skipped for unsupported file type '{file_path}' using GenericFileProcessor." in caplog.text

@pytest.mark.parametrize("file_path", unsupported_files)
def test_generic_save_with_output_path(file_path, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(file_path)
    output_path = tmp_path / Path(file_path).name
    file_obj.save(str(output_path))
    assert f"Saving generic file '{file_path}' to '{output_path}'." in caplog.text
    assert f"Generic file '{file_path}' saved successfully to '{output_path}'." in caplog.text

@pytest.mark.parametrize("file_path", unsupported_files)
def test_generic_save_without_output_path(file_path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(file_path)
    file_obj.save()
    assert f"No output path provided, generic file '{file_path}' was not saved." in caplog.text

@pytest.mark.parametrize("file_path", unsupported_files)
def test_generic_save_failure(file_path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(file_path)
    invalid_path = "/this/does/not/exist/invalid.xyz"
    with pytest.raises(FileProcessingFailedError):
        file_obj.save(invalid_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save generic file" in record.message
        for record in caplog.records
    )
