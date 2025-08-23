import logging
import pytest
from pathlib import Path
from file_processing.errors import FileProcessingFailedError
from file_processing import File
from file_processing_test_data import get_test_files_path
from file_processing.processors.directory_processor import DirectoryProcessor

test_files_path = get_test_files_path()

def test_directory_metadata(temp_directory_with_files, caplog):
    caplog.set_level(logging.DEBUG)
    files_to_copy = [
        test_files_path / "2021_Census_English.csv",
        test_files_path / "SampleReport.pdf",
        test_files_path / "Health_Canada_logo.png",
        test_files_path / "sample.json"
    ]

    temp_dir = temp_directory_with_files(files_to_copy)
    dir_processor = File(str(temp_dir))

    assert dir_processor.metadata['num_items_in_top_level'] == 5  # 4 files + 1 subdirectory
    assert dir_processor.metadata['total_size_of_files_in_top_level'] > 0
    assert 'permissions' in dir_processor.metadata

    assert f"Initializing directory processor for path '{temp_dir}'." in caplog.text
    assert f"Gathered metadata for directory '{temp_dir}'" in caplog.text

def test_list_files_in_top_level(temp_directory_with_files):
    files_to_copy = [
        test_files_path / "2021_Census_English.csv",
        test_files_path / "SampleReport.pdf",
        test_files_path / "Health_Canada_logo.png",
        test_files_path / "sample.json"
    ]

    temp_dir = temp_directory_with_files(files_to_copy)
    dir_processor = File(str(temp_dir))
    files_in_top_level = dir_processor.processor.list_files_in_top_level()

    assert len(files_in_top_level) == 4
    file_names = [f.name for f in files_in_top_level]
    assert sorted(file_names) == ["2021_Census_English.csv", "Health_Canada_logo.png", "SampleReport.pdf", "sample.json"]

    for file_path in files_in_top_level:
        file_obj = File(str(file_path))
        assert file_obj.file_name == file_path.name
        assert file_obj.size > 0

def test_list_subdirectories_in_top_level(temp_directory_with_files):
    files_to_copy = [
        test_files_path / "2021_Census_English.csv",
        test_files_path / "SampleReport.pdf"
    ]

    temp_dir = temp_directory_with_files(files_to_copy)
    dir_processor = File(str(temp_dir))
    subdirs = dir_processor.processor.list_top_level_subdirectories()

    assert len(subdirs) == 1
    assert subdirs[0].name == "subdir"

def test_invalid_directory_path_file_instead_of_directory(caplog):
    caplog.set_level(logging.DEBUG)
    path = test_files_path / "2021_Census_English.csv"  # exists, but is NOT a directory

    with pytest.raises(FileProcessingFailedError):
        DirectoryProcessor(str(path))

    assert any(
        record.levelname == "ERROR" and "Path is not a directory" in record.message
        for record in caplog.records
    )

def test_save_directory_metadata(temp_directory_with_files, caplog):
    caplog.set_level(logging.DEBUG)
    files_to_copy = [
        test_files_path / "2021_Census_English.csv",
        test_files_path / "SampleReport.pdf"
    ]

    temp_dir = temp_directory_with_files(files_to_copy)
    file_obj = File(str(temp_dir))

    # use a Windows-safe invalid path with consistent formatting
    invalid_path = Path("Z:/definitely/nonexistent/save_file.txt")
    with pytest.raises(FileProcessingFailedError):
        file_obj.processor.save(str(invalid_path))

    assert any(
        record.levelname == "ERROR" and "Save location does not exist" in record.message
        for record in caplog.records
    )
