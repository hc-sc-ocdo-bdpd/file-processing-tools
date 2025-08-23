import os
import shutil
import logging
from unittest.mock import patch
from docx import Document
import pytest
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, text_length, last_modified_by, author"
values = [
    (test_files_path / 'HealthCanadaOverviewFromWikipedia.docx', 1631, 'Test last_modified_by One', 'Test Author One'),
    (test_files_path / 'SampleReport.docx', 3220, 'last_modified_by Test Author', 'Second Test Author')
]


@pytest.mark.parametrize(variable_names, values)
def test_docx_metadata(path, text_length, last_modified_by, author, caplog):
    caplog.set_level(logging.DEBUG)

    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['last_modified_by'] == last_modified_by
    assert file_obj.metadata['author'] == author

    assert f"Starting processing of DOCX file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed DOCX file '{file_obj.path}'." in caplog.text


@pytest.mark.parametrize("path, text_length", map(lambda x: x[:2], values))
def test_save_docx_metadata(copy_file, text_length, caplog):
    caplog.set_level(logging.DEBUG)

    docx_file = File(copy_file)
    docx_file.metadata['last_modified_by'] = 'Modified New'
    docx_file.metadata['author'] = 'New Author'
    docx_file.save()

    assert f"Saving DOCX file '{docx_file.path}' to '{docx_file.path}'." in caplog.text
    assert f"DOCX file '{docx_file.path}' saved successfully to '{docx_file.path}'." in caplog.text

    test_docx_metadata(copy_file, text_length, 'Modified New', 'New Author', caplog)


@pytest.mark.parametrize("path, text_length", map(lambda x: x[:2], values))
def test_change_docx_author_last_modified_by(copy_file, text_length, caplog):
    caplog.set_level(logging.DEBUG)

    docx_file = Document(copy_file)
    docx_file.core_properties.last_modified_by = "Modified New"
    docx_file.core_properties.author = "New Author"
    docx_file.save(copy_file)

    test_docx_metadata(copy_file, text_length, 'Modified New', 'New Author', caplog)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_docx_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)

    docx_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        docx_file.processor.save(invalid_save_path)

    assert any(
        record.levelname == "ERROR" and "Failed to save DOCX file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)

    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"DOCX file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


locked_files = [
    (test_files_path / 'SampleReport_Locked.docx'),
    (test_files_path / 'HealthCanadaOverviewFromWikipedia_Locked.docx')
]


@pytest.mark.parametrize("path", locked_files)
def test_docx_locked(path, caplog):
    caplog.set_level(logging.DEBUG)

    file_obj = File(path)
    assert file_obj.metadata["has_password"] is True

    assert f"Starting processing of DOCX file '{file_obj.path}'." in caplog.text
    assert f"DOCX file '{file_obj.path}' is encrypted; skipping text extraction." in caplog.text


@pytest.mark.parametrize("path", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_docx_copy_with_integrity(path, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)

    file_obj = File(path)  # open_file=True by default

    # Logging from initial process
    assert f"Starting processing of DOCX file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed DOCX file '{file_obj.path}'." in caplog.text

    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(path).name
    file_obj.copy(str(dest_path), verify_integrity=True)

    # Logging from copy
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text

    copied = File(str(dest_path))  # triggers new process
    assert f"Starting processing of DOCX file '{copied.path}'." in caplog.text
    assert f"Successfully processed DOCX file '{copied.path}'." in caplog.text

    assert copied.processor.compute_hash(algorithm) == original_hash
    

@pytest.mark.parametrize("path", [v[0] for v in values])
def test_docx_copy_integrity_failure(path, tmp_path, monkeypatch, caplog):
    caplog.set_level(logging.DEBUG)

    file_obj = File(path, open_file=False)

    def corrupt(src, dest, *, follow_symlinks=True):
        with open(dest, 'w') as f:
            f.write("CORRUPTED!")

    monkeypatch.setattr(shutil, "copy2", corrupt)

    dest_path = tmp_path / Path(path).name

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(str(dest_path), verify_integrity=True)

    assert "Integrity check failed" in str(excinfo.value)

    # ✅ Logging from File.copy
    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert any(
        record.levelname == "ERROR" and "Integrity check failed" in record.message
        for record in caplog.records
    )