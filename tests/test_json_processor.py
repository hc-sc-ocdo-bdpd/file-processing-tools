import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from unittest.mock import patch
from errors import FileProcessingFailedError

variable_names = "path, num_keys, key_names, empty_values"
values = [
   ('tests/resources/test_files/coffee.json', 15, ['quiz', 'sport', 'q1', 'question', 'options', 'answer', 'maths', 'q1', 'question', 'options', 'answer', 'q2', 'question', 'options', 'answer'], 0),
   ('tests/resources/test_files/sample.json', 9, ['array', 'boolean', 'color', 'null', 'number', 'object', 'a', 'c', 'string'], 1)
]


@pytest.mark.parametrize(variable_names, values)
def test_json_metadata(path, num_keys, key_names, empty_values):
    file_obj = File(path)
    assert file_obj.metadata['num_keys'] == num_keys
    assert file_obj.metadata['key_names'] == key_names
    assert file_obj.metadata['empty_values'] == empty_values


@pytest.mark.parametrize(variable_names, values)
def test_save_json_metadata(copy_file, num_keys, key_names, empty_values):
    test_json_metadata(copy_file, num_keys, key_names, empty_values)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_html_invalid_save_location(path):
    json_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        json_file.processor.save(invalid_save_path)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()