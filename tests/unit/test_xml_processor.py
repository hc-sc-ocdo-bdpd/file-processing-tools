import os
import logging
import pytest
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, text_length, num_lines, num_words"
values = [
    (test_files_path / 'Sample.xml', 4429, 120, 336)
]


@pytest.mark.parametrize(variable_names, values)
def test_xml_metadata(path, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_lines'] == num_lines
    assert file_obj.metadata['num_words'] == num_words
    assert f"Starting processing of XML file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed XML file '{file_obj.path}'." in caplog.text


@pytest.mark.parametrize(variable_names, values)
def test_save_xml_metadata(copy_file, text_length, num_lines, num_words, caplog):
    caplog.set_level(logging.DEBUG)
    xml_file = File(copy_file)
    save_path = copy_file  # no alt output_path specified
    xml_file.save()
    assert f"Saving XML file '{xml_file.path}' to '{save_path}'." in caplog.text
    assert f"XML file '{xml_file.path}' saved successfully to '{save_path}'." in caplog.text
    test_xml_metadata(copy_file, text_length, num_lines, num_words, caplog)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_xml_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    xml_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        xml_file.save(invalid_save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save XML file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path, open_file=False)
    assert f"XML file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_xml_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_xml_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, "w") as f:
            f.write("corrupted content")

    import shutil
    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / os.path.basename(path), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)