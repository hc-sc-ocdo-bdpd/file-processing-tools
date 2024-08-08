

class FileProcessorError(Exception):
    """Base exception for the file processing library."""


class UnsupportedFileTypeError(FileProcessorError):
    """Raised when an unsupported file type is encountered."""


class FileProcessingFailedError(FileProcessorError):
    """Raised when there's a generic error during file processing."""


class FileCorruptionError(FileProcessorError):
    """Raised when the file is found to be corrupted."""


class OCRError(FileProcessorError):
    """Base exception for OCR related issues."""


class OCRProcessingError(OCRError):
    """Raised when there's an issue during OCR processing."""


class NotOCRApplicableError(OCRError):
    """Raised when attempting OCR on a file type that doesn't support it."""


class TranscriptionError(FileProcessorError):
    """Base exception for transcription related issues."""


class TranscriptionProcessingError(TranscriptionError):
    """Raised when there's an issue during transcription processing."""


class NotTranscriptionApplicableError(TranscriptionError):
    """Raised when attempting transcription on a file type that doesn't support it."""


class TesseractNotFound(Exception):
    """Raised when Tesseract is either not installed or not added to PATH."""


class EmptySelection(FileProcessorError):
    """Raised when the input directory is empty. This may be caused by the filter conditions."""


class FileTypeError(FileProcessorError):
    """Raised when the provided file is of the incorrect file type."""


class EncodingModelError(FileProcessorError):
    """Raised when there is no encoding model specified."""


class NotDocumentBasedFile(KeyError):
    """Raised during file similarity testing when the input file does not have a 'text' field."""


class FAISSIndexError(Exception):
    """Base exception for FAISS related issues"""


class UnsupportedHyperparameterError(FAISSIndexError):
    """Raised when a hyperparameter value cannot be used in the FAISS index"""
