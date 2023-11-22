import PyPDF2
import pytesseract
from PIL import Image
from pathlib import Path
import io
import getpass
from .file_processor_strategy import FileProcessorStrategy
from .errors import OCRProcessingError

# Init for tesseract
pytesseract.pytesseract.tesseract_cmd = Path('C:/Users') / getpass.getuser() / 'AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

class OCRDecorator:
    def __init__(self, processor: FileProcessorStrategy) -> None:
        """Initializes the OCRDecorator with a given file processor."""
        self._processor = processor

    def process(self) -> None:
        """Processes the file using the wrapped processor and then applies OCR."""
        self._processor.process()
        ocr_text = self.extract_text_with_ocr()
        self._processor.metadata['ocr_text'] = ocr_text

    def extract_text_with_ocr(self) -> str:
        """Extracts text from the file using OCR.

        Returns:
            str: The extracted text.
        """
        extension = self._processor.extension
            
        if extension == ".pdf":
            return self._ocr_pdf()
        else:
            return self._ocr_image()

    def _ocr_image(self) -> str:
        try:
            image = Image.open(self._processor.file_path)
            ocr_result = pytesseract.image_to_string(image)
            return ocr_result
        except Exception as e:
            raise OCRProcessingError(f"Error during OCR processing: {e}")


    def _ocr_pdf(self) -> str:
        text = ''
        ocrText = ''

        try:
            with open(self._processor.file_path, 'rb') as pdfFileObj:
                reader = PyPDF2.PdfReader(pdfFileObj)
                numPages = len(reader.pages)

                startPage = 0
                endPage = numPages

                for i in range(startPage, endPage):
                    pageObj = reader.pages[i]
                    
                    text += pageObj.extract_text()
                    
                    for image in pageObj.images:
                        ocrText += pytesseract.image_to_string(Image.open(io.BytesIO(image.data)))

                # Combine the extracted text and OCR text
                combined_text = text + "\n" + ocrText
                return combined_text

        except Exception as e:
            raise OCRProcessingError(f"Error during OCR processing: {e}")

    @property
    def file_name(self) -> str:
        """Returns the file name of the processed file."""
        return self._processor.file_name

    @property
    def metadata(self) -> dict:
        """Returns the metadata of the processed file."""
        return self._processor.metadata
