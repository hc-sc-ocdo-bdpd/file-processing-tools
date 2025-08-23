import os
import shutil
import logging
import pytest
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, original_format, mode, width, height"
values = [
    (test_files_path / 'CanadaLogo.tif', 'TIFF', 'RGB', 215, 74),
    (test_files_path / 'MSWordIcon.tiff', 'TIFF', 'RGBA', 79, 106)
]


@pytest.mark.parametrize(variable_names, values)
def test_tif_metadata(path, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert file_obj.metadata['original_format'] == original_format
    assert file_obj.metadata['mode'] == mode
    assert file_obj.metadata['width'] == width
    assert file_obj.metadata['height'] == height
    assert f"Starting processing of TIFF file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed TIFF file '{file_obj.path}'." in caplog.text


@pytest.mark.parametrize(variable_names, values)
def test_save_tif_metadata(copy_file, original_format, mode, width, height, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(copy_file)
    save_path = copy_file
    file_obj.save(save_path)
    assert f"Saving TIFF file '{file_obj.path}' to '{save_path}'." in caplog.text
    assert f"TIFF file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_tif_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    tif_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        tif_file.processor.save(invalid_save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save TIFF file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path, open_file=False)
    assert f"TIFF file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_tif_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_tif_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, "w") as f:
            f.write("corrupted content")

    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / os.path.basename(path), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)