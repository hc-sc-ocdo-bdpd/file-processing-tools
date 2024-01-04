import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from unittest.mock import patch
from errors import FileProcessingFailedError

variable_names = "path, num_files, file_types, file_names"
values = [
   ('tests/resources/test_files/SampleReport.zip', 3, {'docx': 2, 'pptx': 1}, ['SampleReport.docx', 'SampleReport.pptx', 'HealthCanadaOverviewFromWikipedia.docx']),
   ('tests/resources/test_files/Empty.zip', 0, {}, [])
]

@pytest.fixture(params=values, ids=[x[0] for x in values])
def file_obj(request):
    return File(request.param[0])

def test_zip_extraction(file_obj):
    import shutil
    file_obj.processor.extract()

    extraction_dir = os.path.splitext(file_obj.path)[0]
    assert os.path.isdir(extraction_dir)

    extracted_files = os.listdir(extraction_dir)
    expected_files = file_obj.metadata['file_names']
    assert set(extracted_files) == set(expected_files)

    shutil.rmtree(extraction_dir)

def test_zip_save(file_obj):
    import tempfile, zipfile
    with tempfile.TemporaryDirectory() as temp_dir:
        original_zip_path = file_obj.path
        saved_zip_path = os.path.join(temp_dir, 'SavedSampleReport.zip')

        file_obj.processor.save(saved_zip_path)

        assert os.path.exists(saved_zip_path)

        with zipfile.ZipFile(original_zip_path, 'r') as original_zip, zipfile.ZipFile(saved_zip_path, 'r') as saved_zip:
            assert set(original_zip.namelist()) == set(saved_zip.namelist()) # Check contents are still the same

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_zip_invalid_save_location(invalid_save_location):
    invalid_save_location
    pytest.fail("Test not yet implemented")

@pytest.mark.parametrize(variable_names, values)
def test_zip_metadata(path, num_files, file_types, file_names):
    file_obj = File(path)
    assert file_obj.metadata['num_files'] == num_files
    assert file_obj.metadata['file_types'] == file_types
    assert file_obj.metadata['file_names'] == file_names

@pytest.mark.parametrize(variable_names, values)
def test_save_zip_metadata(copy_file, num_files, file_types, file_names):
    test_zip_metadata(copy_file, num_files, file_types, file_names)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_zip_invalid_save_location(path):
    zip_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        zip_file.save(invalid_save_path)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()