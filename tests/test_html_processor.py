import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from unittest.mock import patch
from errors import FileProcessingFailedError


variable_names = "path, text_length, num_lines, num_words"
values = [
   ('tests/resources/test_files/Health - Canada.ca.html', 165405, 3439, 11162)
]


@pytest.mark.parametrize(variable_names, values)
def test_html_metadata(path, text_length, num_lines, num_words):
    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_lines'] == num_lines
    assert file_obj.metadata['num_words'] == num_words


@pytest.mark.parametrize(variable_names, values)
def test_save_html_metadata(copy_file, text_length, num_lines, num_words):
        test_html_metadata(copy_file, text_length, num_lines, num_words)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_html_invalid_save_location(path):
    html_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        html_file.processor.save(invalid_save_path)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()