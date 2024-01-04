import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from unittest.mock import patch
from errors import FileProcessingFailedError

variable_names = "path, sheet_names, active_sheet, data, last_modified_by, creator"
values = [
   ('tests/resources/test_files/Test_excel_file.xlsx', ['Sheet1', 'Sheet2', 'Sheet3'], "Sheet3", 42, 'Burnett, Taylen (HC/SC)', 'Burnett, Taylen (HC/SC)'),
   ('tests/resources/test_files/Government.xlsx', ['Health Canada', 'Government of Canada'], "Government of Canada", 49, 'Prazuch, Karolina (HC/SC)', 'Prazuch, Karolina (HC/SC)')
]


@pytest.mark.parametrize(variable_names, values)
def test_xlsx_metadata(path, sheet_names, active_sheet, data, last_modified_by, creator):
    file_obj = File(path)
    assert file_obj.metadata['sheet_names'] == sheet_names
    assert file_obj.metadata['active_sheet'] == active_sheet
    assert sum(len(file_obj.metadata["data"][x]) for x in file_obj.metadata["data"].keys()) == data
    assert file_obj.metadata['last_modified_by'] == last_modified_by
    assert file_obj.metadata['creator'] == creator


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path):
    with patch('builtins.open', autospec=True) as mock_open:
        File(path, open_file=False)
        mock_open.assert_not_called()


locked_files = [
    ('tests/resources/test_files/Test_excel_file_Locked.xlsx'), 
    ('tests/resources/test_files/StructureofCanadianFederalGovFromWikipedia_Locked.xlsx')
]

@pytest.mark.parametrize("path", locked_files)
def test_xlsx_locked(path):
    assert File(path).metadata["has_password"] == True


@pytest.mark.parametrize("path, sheet_names, active_sheet, data", map(lambda x: x[:4], values))
def test_save_xlsx_metadata(copy_file, sheet_names, active_sheet, data):
        
        # Load and change metadata via File object
        xlsx_file = File(copy_file)
        xlsx_file.metadata['last_modified_by'] = 'Modified Creator'
        xlsx_file.metadata['creator'] = 'New Creator'

        # Save the updated file
        xlsx_file.save()
        test_xlsx_metadata(copy_file, sheet_names, active_sheet, data, 'Modified Creator', 'New Creator')


@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_xlsx_invalid_save_location(path):
    xlsx_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        xlsx_file.save(invalid_save_path)