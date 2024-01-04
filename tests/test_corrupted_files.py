import pytest
import sys, os
sys.path.append(os.path.join(sys.path[0],'file_processing'))
from file_processing.file import File
from errors import FileProcessingFailedError, FileCorruptionError

corrupted_files_processing = [
    'tests/resources/test_files/2021_Census_English_corrupted.csv',
    'tests/resources/test_files/Health - Canada.ca_corrupted.html',
    'tests/resources/test_files/MapCanada_corrupted.jpg',
    'tests/resources/test_files/Test Email_corrupted.msg',
    'tests/resources/test_files/SampleReportScreenShot_corrupted.pdf',
    'tests/resources/test_files/MapCanada_corrupted.png',
    'tests/resources/test_files/callbacks_corrupted.py',
    'tests/resources/test_files/Test_for_RTF_corrupted.rtf',
    'tests/resources/test_files/government_of_canada_wikipedia_corrupted.txt',
    'tests/resources/test_files/Sample_corrupted.xml',
    'tests/resources/test_files/SampleReport_corrupted.zip'
]

@pytest.mark.parametrize("path", corrupted_files_processing)
def test_corrupted_file_processing_error(path):
    with pytest.raises(FileProcessingFailedError) as exc_info:
        File(path)


corrupted_files_corruption = [
    'tests/resources/test_files/HealthCanadaOverviewFromWikipedia_corrupted.docx',
    'tests/resources/test_files/coffee_corrupted.json',
    'tests/resources/test_files/HealthCanadaOverviewFromWikipedia_corrupted.pptx',
    'tests/resources/test_files/Test_excel_file_corrupted.xlsx',
]

@pytest.mark.parametrize("path", corrupted_files_corruption)
def test_corrupted_file_corruption_error(path):
    with pytest.raises(FileCorruptionError) as exc_info:
        File(path)