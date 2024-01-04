import pytest
import os
from pathlib import Path
from file import File
from errors import OCRProcessingError, NotOCRApplciableError

# TO DO:
# Files and ocr results need to be created and filled in.

PDF_SAMPLES = ["tests/resources/test_files/test_ocr_text.pdf", "tests/resources/test_files/test_ocr_text_2.pdf"]
JPEG_SAMPLES = ["tests/resources/test_files/test_ocr_text.jpg", "tests/resources/test_files/test_ocr_text_2.jpg"]
PNG_SAMPLES = ["tests/resources/test_files/test_ocr_text.png", "tests/resources/test_files/test_ocr_text_2.png"]
NON_OCR_APPLICABLE_SAMPLES = ["tests/resources/test_files/Empty.zip", "tests/resources/test_files/Sample.xml"]

EXPECTED_OCR_RESULTS = {
    PDF_SAMPLES[0]: '\nTest OCR text successful!\n',
    PDF_SAMPLES[1]: '\nTest OCR text successful!\n',
    JPEG_SAMPLES[0]: 'Test OCR text successful!\n',
    JPEG_SAMPLES[1]: 'Test OCR text successful!\n',
    PNG_SAMPLES[0]: 'Test OCR text successful!\n',
    PNG_SAMPLES[1]: 'Test OCR text successful!\n',
}

@pytest.fixture(params=PDF_SAMPLES + JPEG_SAMPLES + PNG_SAMPLES)
def ocr_applicable_file(request):
    return request.param, EXPECTED_OCR_RESULTS[request.param]

@pytest.fixture(params=NON_OCR_APPLICABLE_SAMPLES)
def non_ocr_applicable_file(request):
    return request.param

def test_ocr_processing_success(ocr_applicable_file):
    file_path, expected_ocr_result = ocr_applicable_file
    file = File(str(file_path), use_ocr=True)
    assert 'ocr_text' in file.metadata
    assert file.metadata['ocr_text'] == expected_ocr_result

def test_ocr_processing_non_applicable_file(non_ocr_applicable_file):
    with pytest.raises(NotOCRApplciableError):
        File(str(non_ocr_applicable_file), use_ocr=True)

