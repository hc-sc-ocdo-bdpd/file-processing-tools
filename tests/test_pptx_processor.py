import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from pptx import Presentation
from unittest.mock import patch
from errors import FileProcessingFailedError


variable_names = "path, text_length, num_slides, last_modified_by, author"
values = [
   ('tests/resources/test_files/HealthCanadaOverviewFromWikipedia.pptx', 1655, 4, 'Test last_modified_by One', 'Test Author One'),
   ('tests/resources/test_files/SampleReport.pptx', 2037, 5, 'last_modified_by Test Author', 'Second Test Author')
]


@pytest.mark.parametrize(variable_names, values)
def test_pptx_metadata(path, text_length, num_slides, last_modified_by, author):
    file_obj = File(path)
    assert len(file_obj.metadata['text']) == text_length
    assert file_obj.metadata['num_slides'] == num_slides
    assert file_obj.metadata['last_modified_by'] == last_modified_by
    assert file_obj.metadata['author'] == author


@pytest.mark.parametrize("path, text_length, num_slides", map(lambda x: x[:3], values))
def test_change_save_pptx_metadata(copy_file, text_length, num_slides):
        
        # Load and change metadata via File object
        ppt_file = File(copy_file)
        ppt_file.metadata['last_modified_by'] = 'Modified New'
        ppt_file.metadata['author'] = 'New Author'

        # Save the updated file
        ppt_file.save()
        test_pptx_metadata(copy_file, text_length, num_slides, 'Modified New', 'New Author')


@pytest.mark.parametrize("path, text_length, num_slides", map(lambda x: x[:3], values))
def test_change_pptx_author_last_modified_by(copy_file, text_length, num_slides):
        
        # Change metadata via Presentation object
        ppt_file = Presentation(copy_file)
        ppt_file.core_properties.last_modified_by = "Modified New"
        ppt_file.core_properties.author = "New Author"

        # Save the updated file and load as File object
        ppt_file.save(copy_file)
        test_pptx_metadata(copy_file, text_length, num_slides, 'Modified New', 'New Author')


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_pptx_invalid_save_location(path):
    pptx_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        pptx_file.processor.save(invalid_save_path)


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()


locked_files = [
    ('tests/resources/test_files/SampleReport_Locked.pptx'), 
    ('tests/resources/test_files/HealthCanadaOverviewFromWikipedia_Locked.pptx')
]

@pytest.mark.parametrize("path", locked_files)
def test_pptx_locked(path):
    assert File(path).metadata["has_password"] == True