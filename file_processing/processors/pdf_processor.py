from pypdf import PdfReader, PdfWriter
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy
import logging

logger = logging.getLogger(__name__)

class PdfFileProcessor(FileProcessorStrategy):
    """
    Processor for handling PDF files, extracting metadata such as text content, author,
    and producer, and handling encrypted PDFs.

    Attributes:
        metadata (dict): Contains metadata fields such as 'text', 'has_password', 'author', and
                         'producer' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the PdfFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the PDF file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized with default values.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else self._default_metadata()

    def _default_metadata(self) -> dict:
        """
        Returns default metadata for an unopened PDF file.

        Returns:
            dict: Default metadata with 'text' as None and 'has_password' as False.
        """
        return {
            'text': None,
            'has_password': False
        }

    def process(self) -> None:
        """
        Extracts metadata from the PDF file, including text content, author, and producer.
        Updates metadata if the file is encrypted.

        Raises:
            FileProcessingFailedError: If an error occurs during PDF file processing.
        """
        logger.info(f"Starting processing of PDF file '{self.file_path}'.")
        reader = None
        metadata = {}

        if not self.open_file:
            logger.debug(f"PDF file '{self.file_path}' was not opened (open_file=False).")
            return

        try:
            reader = PdfReader(self.file_path)
            logger.debug(f"PDF file '{self.file_path}' successfully opened.")
        except Exception as e:
            logger.error(f"Failed to process PDF file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while opening {self.file_path}: {e}"
            )

        if not reader.is_encrypted:
            metadata = reader.metadata if reader else {}
            self.metadata.update({
                'text': self.extract_text_from_pdf(reader),
                'author': str(metadata.get('/Author')),
                'producer': str(metadata.get('/Producer'))
            })
            logger.debug(f"Extracted metadata from '{self.file_path}': "
                         f"Author='{self.metadata.get('author')}', "
                         f"Producer='{self.metadata.get('producer')}'")
        else:
            self.metadata['has_password'] = True
            logger.debug(f"PDF file '{self.file_path}' is encrypted; skipping text extraction.")

        logger.info(f"Successfully processed PDF file '{self.file_path}'.")

    def save(self, output_path: str = None) -> None:
        """
        Saves the PDF file to the specified output path.

        Args:
            output_path (str): Path to save the PDF file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If the PDF is encrypted or an error occurs while saving the file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving PDF file '{self.file_path}' to '{save_path}'.")

        try:
            pdf_read = PdfReader(self.file_path)
            if pdf_read.is_encrypted:
                logger.error(f"Failed to save PDF file '{self.file_path}' to '{save_path}': PDF is encrypted.")
                raise FileProcessingFailedError(
                    f"Cannot save encrypted PDF {self.file_path} without password."
                )

            pdf = PdfWriter()
            for page in pdf_read.pages:
                pdf.add_page(page)

            with open(save_path, 'wb') as output_pdf:
                pdf.write(output_pdf)

            logger.info(f"PDF file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save PDF file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving to {save_path}: {e}"
            )

    def extract_text_from_pdf(self, reader: PdfReader) -> str:
        """
        Extracts text from each page of the PDF.

        Args:
            reader (PdfReader): An instance of `PdfReader` for the PDF file.

        Returns:
            str: Extracted text from the PDF pages.

        Raises:
            FileProcessingFailedError: If an error occurs while extracting text.
        """
        try:
            text = ""
            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                except UnboundLocalError as e:
                    logger.warning(f"Failed to extract text from page {page_number} in {self.file_path}: {e}")
                    continue
            return text
        except Exception as e:
            logger.error(f"Failed to process PDF file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while extracting text from {self.file_path}: {e}"
            )