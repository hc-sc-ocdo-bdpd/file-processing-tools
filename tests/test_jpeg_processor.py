import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from unittest.mock import patch
from errors import FileProcessingFailedError


variable_names = "path, original_format, mode, width, height"
values = [
   ('tests/resources/test_files/HealthCanada.jpeg', 'JPEG', 'RGB', 474, 262),
   ('tests/resources/test_files/MapCanada.jpg', 'JPEG', 'RGB', 4489, 2896)
]


@pytest.mark.parametrize(variable_names, values)
def test_jpeg_metadata(path, original_format, mode, width, height):
    file_obj = File(path)
    assert file_obj.metadata['original_format'] == original_format
    assert file_obj.metadata['mode'] == mode
    assert file_obj.metadata['width'] == width
    assert file_obj.metadata['height'] == height


@pytest.mark.parametrize(variable_names, values)
def test_save_jpeg_metadata(copy_file, original_format, mode, width, height):
    test_jpeg_metadata(copy_file, original_format, mode, width, height)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_jpeg_invalid_save_location(path):
    jpeg_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        jpeg_file.processor.save(invalid_save_path)
    

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()