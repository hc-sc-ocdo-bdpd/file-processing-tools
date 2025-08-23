from pathlib import Path
import shutil
import pytest
from file_processing import File
from file_processing.errors import FileProcessingFailedError

# Shared fixture to create a temporary directory structure with specified files from file-processing-test-data
@pytest.fixture()
def temp_directory_with_files(tmp_path_factory):
    def _create_temp_dir(files):
        temp_dir = tmp_path_factory.mktemp("temp_dir")

        # Copy specified files from file-processing-test-data into the temp directory
        for file_path in files:
            shutil.copy(file_path, temp_dir)

        # Create subdirectories for testing if needed (empty or with files)
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        return temp_dir

    return _create_temp_dir

# Fixture for copying files
@pytest.fixture()
def copy_file(path, tmp_path_factory):
    copy_path = str(tmp_path_factory.mktemp("copy") / Path(path).name)
    file_obj = File(path)
    file_obj.save(copy_path)
    yield copy_path

# Fixture for invalid save locations
@pytest.fixture()
def invalid_save_location(path):
    save_path = '/non_existent_folder/' + path
    file_obj = File(path)
    with pytest.raises(FileProcessingFailedError):
        file_obj.processor.save(save_path)
