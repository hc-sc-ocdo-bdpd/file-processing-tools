import os
import shutil
import logging
import pytest
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, sheet_names, active_sheet, data, last_modified_by, creator"
values = [
    (test_files_path / 'Test_excel_file.xlsx', ['Sheet1', 'Sheet2', 'Sheet3'], "Sheet3", 42,
     'Burnett, Taylen (HC/SC)', 'Burnett, Taylen (HC/SC)'),
    (test_files_path / 'Government.xlsx', ['Health Canada', 'Government of Canada'],
     "Government of Canada", 49, 'Prazuch, Karolina (HC/SC)', 'Prazuch, Karolina (HC/SC)')
]


@pytest.mark.parametrize(variable_names, values)
def test_xlsx_metadata(path, sheet_names, active_sheet, data, last_modified_by, creator, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    assert file_obj.metadata['sheet_names'] == sheet_names
    assert file_obj.metadata['active_sheet'] == active_sheet
    assert sum(len(file_obj.metadata["data"][x]) for x in file_obj.metadata["data"].keys()) == data
    assert file_obj.metadata['last_modified_by'] == last_modified_by
    assert file_obj.metadata['creator'] == creator
    assert f"Starting processing of XLSX file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed XLSX file '{file_obj.path}'." in caplog.text


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path, open_file=False)
    assert f"XLSX file '{file_obj.path}' was not opened (open_file=False)." in caplog.text


locked_files = [
    test_files_path / 'Test_excel_file_Locked.xlsx',
    test_files_path / 'StructureofCanadianFederalGovFromWikipedia_Locked.xlsx'
]


@pytest.mark.parametrize("path", locked_files)
def test_xlsx_locked(path):
    assert File(path).metadata["has_password"] is True


@pytest.mark.parametrize("path, sheet_names, active_sheet, data", map(lambda x: x[:4], values))
def test_save_xlsx_metadata(copy_file, sheet_names, active_sheet, data, caplog):
    caplog.set_level(logging.DEBUG)
    xlsx_file = File(copy_file)
    xlsx_file.metadata['last_modified_by'] = 'Modified Creator'
    xlsx_file.metadata['creator'] = 'New Creator'
    save_path = copy_file  # no alt output_path specified
    xlsx_file.save()
    assert f"Saving XLSX file '{xlsx_file.path}' to '{save_path}'." in caplog.text
    assert f"XLSX file '{xlsx_file.path}' saved successfully to '{save_path}'." in caplog.text
    test_xlsx_metadata(copy_file, sheet_names, active_sheet, data, 'Modified Creator', 'New Creator', caplog)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_xlsx_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    xlsx_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        xlsx_file.save(invalid_save_path)
    assert any(
        record.levelname == "ERROR" and "Failed to save XLSX file" in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_xlsx_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
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
def test_xlsx_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, "w") as f:
            f.write("corrupted content")

    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / os.path.basename(path), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)