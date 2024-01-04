import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0], 'file_processing'))
from file import File
from unittest.mock import patch
from errors import FileProcessingFailedError


variable_names = "path, num_lines, num_functions, num_classes, num_imports, num_docstrings"
values = [
   ('tests/resources/test_files/backend.py', 6503, 224, 5, 69, 194),
   ('tests/resources/test_files/align.py', 213, 8, 0, 16, 3)
]


@pytest.mark.parametrize(variable_names, values)
def test_python_metadata(path, num_lines, num_functions, num_classes, num_imports, num_docstrings):
    file_obj = File(path)
    assert file_obj.metadata['num_lines'] == num_lines
    assert file_obj.metadata['num_functions'] == num_functions
    assert file_obj.metadata['num_classes'] == num_classes
    assert len(file_obj.metadata['imports']) == num_imports
    assert len(file_obj.metadata['docstrings']) == num_docstrings


@pytest.mark.parametrize(variable_names, values)
def test_not_opening_file(path, num_lines, num_functions, num_classes, num_imports, num_docstrings):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()


@pytest.fixture()
def copy_file(path, tmp_path_factory):
    from pathlib import Path
    copy_path = str(tmp_path_factory.mktemp("copy") / Path(path).name)
    file_obj = File(path)
    file_obj.save(copy_path)
    yield copy_path


@pytest.mark.parametrize(variable_names, values)
def test_save_python_metadata(copy_file, num_lines, num_functions, num_classes, num_imports, num_docstrings):
    test_python_metadata(copy_file, num_lines, num_functions, num_classes, num_imports, num_docstrings)


invalid_save_locations_python = [
    ('tests/resources/test_files/backend.py', '/non_existent_folder/backend.py')
]


@pytest.mark.parametrize("path, save_path", invalid_save_locations_python)
def test_py_invalid_save_location(path, save_path):
    file_obj = File(path)
    with pytest.raises(FileProcessingFailedError):
        file_obj.save(save_path)