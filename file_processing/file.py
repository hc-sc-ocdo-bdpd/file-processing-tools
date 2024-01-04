from pathlib import Path
from txt_processor import TextFileProcessor
from pdf_processor import PdfFileProcessor
from docx_processor import DocxFileProcessor
from ocr_decorator import OCRDecorator
from msg_processor import MsgFileProcessor
from png_processor import PngFileProcessor
from xlsx_processor import xlsxFileProcessor
from pptx_processor import PptxFileProcessor
from rtf_processor import RtfFileProcessor
from html_processor import HtmlFileProcessor
from xml_processor import XmlFileProcessor
from jpeg_processor import JpegFileProcessor
from csv_processor import CsvFileProcessor
from json_processor import JsonFileProcessor
from zip_processor import ZipFileProcessor
from audio_processor import AudioFileProcessor
from transcription_decorator import TranscriptionDecorator
from generic_processor import GenericFileProcessor
from py_processor import PyFileProcessor
from errors import UnsupportedFileTypeError, NotOCRApplciableError, NotTranscriptionApplicableError

class File:
    OCR_APPLICABLE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
    TRANSCRIPTION_APPLICABLE_EXTENSIONS = {".mp3", ".wav", ".mp4", ".flac", ".aiff", ".ogg"}

    PROCESSORS = {
        ".csv": CsvFileProcessor,
        ".txt": TextFileProcessor,
        ".pdf": PdfFileProcessor,
        ".docx": DocxFileProcessor,
        ".msg": MsgFileProcessor,
        ".pptx": PptxFileProcessor,
        ".rtf": RtfFileProcessor,
        ".html": HtmlFileProcessor,
        ".xml": XmlFileProcessor,
        ".png": PngFileProcessor,
        ".xlsx": xlsxFileProcessor,
        ".jpeg": JpegFileProcessor,
        ".jpg": JpegFileProcessor,
        ".json": JsonFileProcessor,
        ".zip": ZipFileProcessor,
        ".mp3": AudioFileProcessor,
        ".wav": AudioFileProcessor,
        ".mp4": AudioFileProcessor,
        ".flac": AudioFileProcessor,
        ".aiff": AudioFileProcessor,
        ".ogg": AudioFileProcessor,
        ".py": PyFileProcessor
    }

    def __init__(self, path: str, use_ocr: bool = False, use_transcriber: bool = False, open_file: bool = True) -> None:
        self.path = Path(path)
        self.processor = self._get_processor(use_ocr, use_transcriber, open_file)
        self.process()

    def _get_processor(self, use_ocr: bool, use_transcriber: bool, open_file: bool) -> 'FileProcessorStrategy':
        extension = self.path.suffix
        processor_class = File.PROCESSORS.get(extension, GenericFileProcessor)
        processor = processor_class(str(self.path), open_file)

        if use_ocr:
            if extension not in File.OCR_APPLICABLE_EXTENSIONS:
                raise NotOCRApplciableError(f"OCR is not applicable for file type {extension}.")
            return OCRDecorator(processor)
        
        if use_transcriber:
            if extension not in File.TRANSCRIPTION_APPLICABLE_EXTENSIONS:
                raise NotTranscriptionApplicableError(f"Transcription is not applicable for file type {extension}.")
            return TranscriptionDecorator(processor)

        return processor



    def save(self, output_path: str = None) -> None:
        self.processor.save(output_path)


    def process(self) -> None:
        return self.processor.process()

    
    @property
    def file_path(self) -> str:
        return self.processor.file_path


    @property
    def file_name(self) -> str:
        return self.processor.file_name


    @property
    def extension(self) -> str:
        return self.processor.extension

    @property
    def size(self) -> str:
        return self.processor.size

    @property
    def modification_time(self) -> str:
        return self.processor.modification_time

    @property
    def access_time(self) -> str:
        return self.processor.access_time

    @property
    def metadata(self) -> dict:
        return self.processor.metadata
