import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from unittest.mock import patch
from errors import FileProcessingFailedError

# Note: test_save_png_metadata tests both files for "original_format == 'PNG'
# when creating a copy, the original_format metadata for Health_Canada_logo.png
# becomes 'GIF' --> 'PNG'

variable_names = "path, original_format, mode, width, height"
values = [
   ('tests/resources/test_files/Health_Canada_logo.png', 'GIF', 'P', 303, 40),
   ('tests/resources/test_files/MapCanada.png', 'PNG', 'RGBA', 3000, 2408)
]


@pytest.mark.parametrize(variable_names, values)
def test_png_metadata(path, original_format, mode, width, height):
    file_obj = File(path)
    assert file_obj.metadata['original_format'] == original_format
    assert file_obj.metadata['mode'] == mode
    assert file_obj.metadata['width'] == width
    assert file_obj.metadata['height'] == height


@pytest.mark.parametrize(variable_names, values)
def test_save_png_metadata(copy_file, original_format, mode, width, height):
    test_png_metadata(copy_file, 'PNG', mode, width, height)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_png_invalid_save_location(path):
    png_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        png_file.processor.save(invalid_save_path)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()