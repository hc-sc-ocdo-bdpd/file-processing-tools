import os
import shutil
import logging
from unittest.mock import patch
import tempfile
from pathlib import Path
import pytest
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

# Sample metadata to check against
variable_names = "path, entry_point, machine, num_sections"
values = [
    (test_files_path / 'hello-world.exe', '0xc320', '0x8664', 6)
]

@pytest.fixture(params=values, ids=[str(x[0]) for x in values])
def exe_file_obj(request):
    return File(request.param[0])

def test_exe_metadata(caplog):
    caplog.set_level(logging.DEBUG)

    file_obj = File(str(test_files_path / "hello-world.exe"))

    assert file_obj.metadata['entry_point'] == file_obj.metadata.get('entry_point')
    assert file_obj.metadata['machine'] == file_obj.metadata.get('machine')
    assert file_obj.metadata['num_sections'] == file_obj.metadata.get('num_sections')

    assert f"Starting processing of EXE file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed EXE file '{file_obj.path}'." in caplog.text

def test_exe_save(exe_file_obj, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as temp_dir:
        original_exe_path = exe_file_obj.path
        saved_exe_path = os.path.join(temp_dir, 'SavedSampleApp.exe')

        exe_file_obj.processor.save(saved_exe_path)

        assert os.path.exists(saved_exe_path)
        assert os.path.getsize(saved_exe_path) == os.path.getsize(original_exe_path)

        assert f"Saving EXE file '{exe_file_obj.path}' to '{saved_exe_path}'." in caplog.text
        assert f"EXE file '{exe_file_obj.path}' saved successfully to '{saved_exe_path}'." in caplog.text

@pytest.mark.parametrize(variable_names, values)
def test_exe_file_processing(path, entry_point, machine, num_sections, caplog):
    caplog.set_level(logging.DEBUG)

    exe_file_obj = File(path)
    assert exe_file_obj.metadata['entry_point'] == entry_point
    assert exe_file_obj.metadata['machine'] == machine
    assert exe_file_obj.metadata['num_sections'] == num_sections

    assert f"Starting processing of EXE file '{exe_file_obj.path}'." in caplog.text
    assert f"Successfully processed EXE file '{exe_file_obj.path}'." in caplog.text

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_exe_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)

    exe_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        exe_file.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save EXE file" in record.message
        for record in caplog.records
    )

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_exe_file(path, caplog):
    caplog.set_level(logging.DEBUG)

    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"EXE file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("path", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_exe_copy_with_integrity(path, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)

    file_obj = File(path)  # open_file=True to ensure processing occurs

    # ✅ Processor logging
    assert f"Starting processing of EXE file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed EXE file '{file_obj.path}'." in caplog.text

    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(path).name
    file_obj.copy(str(dest_path), verify_integrity=True)

    # ✅ Logging from File.copy()
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text

    copied = File(str(dest_path))  # open_file=True by default

    # ✅ Logging for copied file
    assert f"Starting processing of EXE file '{copied.path}'." in caplog.text
    assert f"Successfully processed EXE file '{copied.path}'." in caplog.text

    # ✅ Data integrity
    assert copied.processor.compute_hash(algorithm) == original_hash
    assert copied.metadata.get("entry_point") is not None
    assert copied.metadata.get("machine") is not None

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_exe_copy_integrity_failure(path, tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)

    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    dest_path = tmp_path / Path(path).name

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(dest_path), verify_integrity=True)

    # ✅ Error message and log
    assert "Integrity check failed" in str(excinfo.value)
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert any(
        record.levelname == "ERROR" and "Integrity check failed" in record.message
        for record in caplog.records
    )
