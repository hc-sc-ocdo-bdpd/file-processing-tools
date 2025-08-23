from pathlib import Path
from file_processing import processors
from file_processing.file_processor_strategy import FileProcessorStrategy
from file_processing.errors import (
    FileProcessingFailedError,
    TesseractNotFound,
    NotOCRApplicableError,
    NotTranscriptionApplicableError,
    OptionalDependencyNotInstalledError
)
import shutil
import logging

logger = logging.getLogger(__name__)  

class File:
    """
    Represents a file to be processed, with support for OCR, transcription, and various file types.
    This class applies the Strategy Pattern to dynamically select an appropriate file processor based on
    the file extension.

    Attributes:
        OCR_APPLICABLE_EXTENSIONS (set): File extensions suitable for OCR processing.
        TRANSCRIPTION_APPLICABLE_EXTENSIONS (set): File extensions suitable for transcription processing.
        PROCESSORS (dict): Mapping of file extensions to their respective processor classes.

    Methods:
        save(output_path): Saves the processed file to the specified output path.
        process(): Processes the file using the selected processor.
    """

    OCR_APPLICABLE_EXTENSIONS = {".pdf", ".jpeg", ".jpg", ".png", ".gif", ".tiff", ".tif"}
    TRANSCRIPTION_APPLICABLE_EXTENSIONS = {".mp3", ".wav", ".mp4", ".flac", ".aiff", ".ogg"}

    PROCESSORS = {
        ".cpp": processors.CppFileProcessor,
        ".cc": processors.CppFileProcessor,
        ".csv": processors.CsvFileProcessor,
        ".js": processors.JsFileProcessor,
        ".txt": processors.TextFileProcessor,
        ".pdf": processors.PdfFileProcessor,
        ".docx": processors.DocxFileProcessor,
        ".h": processors.HFileProcessor,
        ".go": processors.GoFileProcessor,
        ".msg": processors.MsgFileProcessor,
        ".pptx": processors.PptxFileProcessor,
        ".rtf": processors.RtfFileProcessor,
        ".html": processors.HtmlFileProcessor,
        ".xml": processors.XmlFileProcessor,
        ".png": processors.PngFileProcessor,
        ".xlsx": processors.XlsxFileProcessor,
        ".java": processors.JavaFileProcessor,
        ".jpeg": processors.JpegFileProcessor,
        ".jpg": processors.JpegFileProcessor,
        ".json": processors.JsonFileProcessor,
        ".zip": processors.ZipFileProcessor,
        ".mp3": processors.AudioFileProcessor,
        ".wav": processors.AudioFileProcessor,
        ".mp4": processors.AudioFileProcessor,
        ".flac": processors.AudioFileProcessor,
        ".rb": processors.RbFileProcessor,
        ".aiff": processors.AudioFileProcessor,
        ".ogg": processors.AudioFileProcessor,
        ".py": processors.PyFileProcessor,
        ".gif": processors.GifFileProcessor,
        ".tif": processors.TiffFileProcessor,
        ".tiff": processors.TiffFileProcessor,
        ".heic": processors.HeicFileProcessor,
        ".heif": processors.HeicFileProcessor,
        ".gguf": processors.GgufFileProcessor,
        ".gitignore": processors.GitignoreFileProcessor,
        ".ipynb": processors.IpynbFileProcessor,
        ".exe": processors.ExeFileProcessor,
        ".whl": processors.WhlFileProcessor
    }

    def __init__(self, path: str, use_ocr: bool = False, ocr_path: str = None, 
                 use_transcriber: bool = False, open_file: bool = True) -> None:
        """
        Initializes the File object with the specified path and optional OCR and transcription capabilities.

        Args:
            path (str): The file path to process.
            use_ocr (bool): Flag to enable OCR processing if applicable.
            ocr_path (str): Optional path to Tesseract OCR executable.
            use_transcriber (bool): Flag to enable transcription if applicable.
            open_file (bool): Indicates whether the file should be opened immediately.
        """
        self.path = Path(path)
        self.processor = self._get_processor(use_ocr, ocr_path, use_transcriber, open_file)
        self.process()
        
    def _get_processor(self, use_ocr: bool, ocr_path: str,
                       use_transcriber: bool, open_file: bool) -> FileProcessorStrategy:
        """
        Determines and returns the appropriate processor for the file based on its extension.

        Args:
            use_ocr (bool): Whether to use OCR processing.
            ocr_path (str): Path to the OCR executable.
            use_transcriber (bool): Whether to use transcription.
            open_file (bool): Whether to open the file immediately.

        Returns:
            FileProcessorStrategy: An instance of a file processor suitable for the file type.

        Raises:
            NotOCRApplicableError: If OCR is requested but not supported for the file type.
            OptionalDependencyNotInstalledError: If an optional library for OCR or transcription is not installed.
            TesseractNotFound: If Tesseract OCR is not installed or configured.
            NotTranscriptionApplicableError: If transcription is requested but not supported for the file type.
        """
        if self.path.is_dir():
            return processors.DirectoryProcessor(str(self.path), open_file)

        extension = self.path.suffix
        processor_class = File.PROCESSORS.get(extension, processors.GenericFileProcessor)
        processor = processor_class(str(self.path), open_file)

        if use_ocr:
            if extension not in File.OCR_APPLICABLE_EXTENSIONS:
                raise NotOCRApplicableError(f"OCR is not applicable for file type {extension}.")
            try:
                from file_processing_ocr.ocr_decorator import OCRDecorator
                import pytesseract

                if ocr_path:
                    pytesseract.pytesseract.tesseract_cmd = ocr_path
                pytesseract.get_tesseract_version()
            except ImportError:
                raise OptionalDependencyNotInstalledError("OCR functionality requires the 'file-processing-ocr' library. "
                                                        "Please install it using 'pip install file-processing-ocr'.")
            except Exception:
                raise TesseractNotFound(f"Tesseract is not installed or not added to PATH. Path: {pytesseract.pytesseract.tesseract_cmd}")

            return OCRDecorator(processor, ocr_path)

        if use_transcriber:
            try:
                from file_processing_transcription.transcription_decorator import TranscriptionDecorator
                if extension not in File.TRANSCRIPTION_APPLICABLE_EXTENSIONS:
                    raise NotTranscriptionApplicableError(
                        f"Transcription is not applicable for file type {extension}.")
            except ImportError:
                raise OptionalDependencyNotInstalledError("Transcription functionality requires the 'file-processing-transcription' library. "
                                                        "Please install it using 'pip install file-processing-transcription'.")

            return TranscriptionDecorator(processor)

        return processor

    def save(self, output_path: str = None) -> None:
        """
        Saves the processed file to the specified output path.

        Args:
            output_path (str): Destination path (defaults to original file path).
        """
        self.processor.save(output_path)

    def copy(self, output_path: str, verify_integrity: bool = False) -> None:
        """
        Copies the original file bit-for-bit.

        Args:
            output_path (str): Destination path (defaults to original file path).
            verify_integrity (bool): If True, re-compute and compare hash after copy.
        """
        logger.info(f"Copying file from '{self.file_path}' to '{output_path}' with integrity verification={verify_integrity}.")  
  
        original_hash = self.hash if verify_integrity else None  
        src = self.processor.file_path  
        shutil.copy2(str(src), str(output_path))  
    
        if verify_integrity:  
            copied = File(str(output_path), open_file=False)  
            copied_hash = copied.hash  
            logger.info(f"Original SHA256 hash: {original_hash}")  
            logger.info(f"Copied file SHA256 hash: {copied_hash}")  
            if original_hash != copied_hash:  
                logger.error(f"Integrity check failed for '{output_path}': original hash '{original_hash}' does not match copied hash '{copied_hash}'.")  
                raise FileProcessingFailedError(  
                    f"Integrity check failed on copy: {output_path} hash changed "  
                    f"({original_hash} → {copied_hash})"  
                )  
            else:  
                logger.info(f"Integrity verification passed for '{output_path}'.")

    def process(self) -> None:
        """
        Executes the processing operation on the file.
        """
        return self.processor.process()

    # Property methods with docstrings for Sphinx documentation
    @property
    def file_path(self) -> str:
        """str: Returns the file path of the processed file."""
        return self.processor.file_path

    @property
    def file_name(self) -> str:
        """str: Returns the name of the file."""
        return self.processor.file_name

    @property
    def extension(self) -> str:
        """str: Returns the file extension."""
        return self.processor.extension

    @property
    def owner(self) -> str:
        """str: Returns the owner of the file."""
        return self.processor.owner

    @property
    def size(self) -> int:
        """int: Returns the size of the file in bytes."""
        return self.processor.size

    @property
    def modification_time(self) -> float:
        """float: Returns the last modification time of the file."""
        return self.processor.modification_time

    @property
    def access_time(self) -> float:
        """float: Returns the last access time of the file."""
        return self.processor.access_time

    @property
    def creation_time(self) -> float:
        """float: Returns the creation time of the file."""
        return self.processor.creation_time

    @property
    def parent_directory(self) -> str:
        """str: Returns the parent directory of the file."""
        return self.processor.parent_directory

    @property
    def permissions(self) -> str:
        """str: Returns the file permissions."""
        return self.processor.permissions

    @property
    def is_file(self) -> bool:
        """bool: Checks if the path points to a regular file."""
        return self.processor.is_file

    @property
    def is_symlink(self) -> bool:
        """bool: Checks if the file is a symbolic link."""
        return self.processor.is_symlink

    @property
    def absolute_path(self) -> str:
        """str: Returns the absolute path of the file."""
        return self.processor.absolute_path
    
    @property
    def hash(self) -> str:
        """str: Hex digest of this file's content (default SHA256)."""
        return self.processor.hash

    @property
    def metadata(self) -> dict:
        """dict: Returns the metadata of the file."""
        return self.processor.metadata
