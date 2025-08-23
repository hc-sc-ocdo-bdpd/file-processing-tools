import os
import shutil
import logging
from unittest.mock import patch
import pytest
from pathlib import Path
from pptx import Presentation
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, text_length, num_slides, last_modified_by, author"
values = [
    (test_files_path / 'HealthCanadaOverviewFromWikipedia.pptx', 1655, 4, 'Test last_modified_by One', 'Test Author One'),
    (test_files_path / 'SampleReport.pptx', 2037, 5, 'last_modified_by Test Author', 'Second Test Author')
]


@pytest.mark.parametrize(variable_names, values)
def test_pptx_metadata(path, text_length, num_slides, last_modified_by, author, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_slides'] == num_slides
    assert file_obj.metadata['last_modified_by'] == last_modified_by
    assert file_obj.metadata['author'] == author
    assert f"Starting processing of PPTX file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed PPTX file '{file_obj.path}'." in caplog.text


@pytest.mark.parametrize("path, text_length, num_slides", map(lambda x: x[:3], values))
def test_change_save_pptx_metadata(copy_file, text_length, num_slides, caplog):
    caplog.set_level(logging.DEBUG)
    ppt_file = File(copy_file)
    ppt_file.metadata['last_modified_by'] = 'Modified New'
    ppt_file.metadata['author'] = 'New Author'
    ppt_file.save()
    save_path = str(copy_file)
    assert f"Saving PPTX file '{ppt_file.path}' to '{save_path}'." in caplog.text
    assert f"PPTX file '{ppt_file.path}' saved successfully to '{save_path}'." in caplog.text
    test_pptx_metadata(copy_file, text_length, num_slides, 'Modified New', 'New Author', caplog)


@pytest.mark.parametrize("path, text_length, num_slides", map(lambda x: x[:3], values))
def test_change_pptx_author_last_modified_by(copy_file, text_length, num_slides, caplog):
    caplog.set_level(logging.DEBUG)
    ppt_file = Presentation(copy_file)
    ppt_file.core_properties.last_modified_by = "Modified New"
    ppt_file.core_properties.author = "New Author"
    ppt_file.save(copy_file)
    test_pptx_metadata(copy_file, text_length, num_slides, 'Modified New', 'New Author', caplog)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_pptx_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    pptx_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        pptx_file.processor.save(invalid_save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save PPTX file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"PPTX file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


locked_files = [
    (test_files_path / 'SampleReport_Locked.pptx'),
    (test_files_path / 'HealthCanadaOverviewFromWikipedia_Locked.pptx')
]


@pytest.mark.parametrize("path", locked_files)
def test_pptx_locked(path, caplog):
    caplog.set_level(logging.DEBUG)
    assert File(path).metadata["has_password"] is True
    assert "is encrypted" in caplog.text


@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_pptx_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_pptx_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, "w") as f:
            f.write("corrupted pptx data")

    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / Path(path).name, verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)