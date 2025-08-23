import os  
import shutil  
import pytest  
import logging  
from pathlib import Path  
from file_processing import File  
from file_processing.errors import FileProcessingFailedError  
from file_processing_test_data import get_test_files_path  
  
test_files_path = get_test_files_path()  
  
variable_names = (  
    "path, text_present, has_password, author, producer, "  
    "expect_exception_on_process, expect_exception_on_save"  
)  
  
values = [  
    # Unencrypted PDFs  
    (test_files_path / 'ArtificialNeuralNetworksForBeginners.pdf', True, False, None, None, False, False),  
    (test_files_path / 'HealthCanadaOverviewFromWikipedia.pdf', True, False, None, None, False, False),  
    (test_files_path / 'SampleReport.pdf', True, False, None, None, False, False),  
    (test_files_path / 'SampleReportScreenShot.pdf', True, False, None, None, False, False),  
    # Encrypted PDFs  
    (test_files_path / 'ArtificialNeuralNetworksForBeginners_Locked.pdf', False, True, None, None, False, True),  
    (test_files_path / 'SampleReport_Locked.pdf', False, True, None, None, False, True),  
    # Corrupted PDF  
    (test_files_path / 'SampleReportScreenShot_corrupted.pdf', False, False, None, None, True, True),  
]  
  
@pytest.mark.parametrize(variable_names, values)  
def test_pdf_metadata(  
    path,  
    text_present,  
    has_password,  
    author,  
    producer,  
    expect_exception_on_process,  
    expect_exception_on_save,  
    caplog,  
):  
    caplog.set_level(logging.DEBUG)  
  
    if expect_exception_on_process:  
        with pytest.raises(FileProcessingFailedError):  
            File(str(path))  
  
        assert any(  
            record.levelname == "ERROR" and "Failed to process PDF file" in record.message  
            for record in caplog.records  
        )  
    else:  
        file_obj = File(str(path))  
        metadata = file_obj.metadata  
        assert metadata['has_password'] == has_password  
  
        assert f"Starting processing of PDF file '{file_obj.path}'." in caplog.text  
        assert f"Successfully processed PDF file '{file_obj.path}'." in caplog.text  
  
        if text_present:  
            assert metadata['text'] is not None  
            assert len(metadata['text']) > 0  
        else:  
            assert metadata['text'] is None  
  
        if author is not None:  
            assert metadata['author'] == author  
        if producer is not None:  
            assert metadata['producer'] == producer  
  
@pytest.mark.parametrize(variable_names, values)  
def test_save_pdf_metadata(  
    path,  
    text_present,  
    has_password,  
    author,  
    producer,  
    expect_exception_on_process,  
    expect_exception_on_save,  
    tmp_path,  
    caplog,  
):  
    caplog.set_level(logging.DEBUG)  
  
    if expect_exception_on_process:  
        with pytest.raises(FileProcessingFailedError):  
            File(str(path))  
    else:  
        file_obj = File(str(path))  
        save_path = tmp_path / os.path.basename(path)  
  
        if expect_exception_on_save:  
            with pytest.raises(FileProcessingFailedError):  
                file_obj.save(str(save_path))  
  
            assert any(  
                record.levelname == "ERROR" and "Failed to save PDF file" in record.message  
                for record in caplog.records  
            )  
        else:  
            file_obj.save(str(save_path))  
            file_obj_saved = File(str(save_path))  
            metadata = file_obj_saved.metadata  
  
            assert f"Saving PDF file '{file_obj.path}' to '{save_path}'." in caplog.text  
            assert f"PDF file '{file_obj.path}' saved successfully to '{save_path}'." in caplog.text  
  
            assert metadata['has_password'] == has_password  
            if text_present:  
                assert metadata['text'] is not None  
                assert len(metadata['text']) > 0  
            else:  
                assert metadata['text'] is None  
  
            if author is not None:  
                assert metadata['author'] == author  
            if producer is not None:  
                assert metadata['producer'] == producer  
  
@pytest.mark.parametrize("valid_path", [path for path, *_ in values])  
def test_pdf_invalid_save_location(valid_path, caplog):  
    caplog.set_level(logging.DEBUG)  
  
    file_obj = File(str(valid_path), open_file=False)  
    invalid_save_path = '/non_existent_folder/' + os.path.basename(str(valid_path))  
  
    with pytest.raises(FileProcessingFailedError):  
        file_obj.save(invalid_save_path)  
  
    assert any(  
        record.levelname == "ERROR" and "Failed to save PDF file" in record.message  
        for record in caplog.records  
    )  
  
@pytest.mark.parametrize("path", [path for path, *_ in values])  
def test_not_opening_pdf(path, caplog):  
    caplog.set_level(logging.DEBUG)  
  
    file_obj = File(str(path), open_file=False)  
    metadata = file_obj.metadata  
    assert metadata == {'message': 'File was not opened'}  
  
    assert "was not opened (open_file=False)" in caplog.text  
  
@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_pdf_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    path = test_files_path / file_name
    file_obj = File(str(path), open_file=False)

    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(file_name).name
    file_obj.copy(str(dest_path), verify_integrity=True)

    try:
        copied = File(str(dest_path))
        assert copied.processor.compute_hash(algorithm) == original_hash
        assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
        assert f"Integrity verification passed for '{dest_path}'." in caplog.text
    except FileProcessingFailedError:
        # ✅ Expected for corrupted files — assert log message
        assert "Failed to process PDF file" in caplog.text
  
@pytest.mark.parametrize("path", [path for path, *rest in values if not rest[-2]])  # Only non-corrupt  
def test_pdf_copy_integrity_failure(path, tmp_path, monkeypatch):  
    file_obj = File(str(path), open_file=False)  
  
    def corrupt(src, dst, *, follow_symlinks=True):  
        with open(dst, 'w') as f:  
            f.write("INVALID PDF FILE")  
  
    monkeypatch.setattr(shutil, "copy2", corrupt)  
  
    with pytest.raises(FileProcessingFailedError) as excinfo:  
        file_obj.copy(tmp_path / Path(path).name, verify_integrity=True)  
  
    assert "Integrity check failed" in str(excinfo.value)  