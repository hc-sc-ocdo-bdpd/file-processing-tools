import chardet
import logging
from file_processing.file_processor_strategy import FileProcessorStrategy
from file_processing.errors import FileProcessingFailedError

logger = logging.getLogger(__name__)

class HtmlFileProcessor(FileProcessorStrategy):
    """
    Processor for handling HTML files, extracting text content and metadata such as encoding,
    line count, and word count.

    Attributes:
        metadata (dict): Contains metadata fields including 'text', 'encoding', 'lines', 'words',
                         'num_lines', and 'num_words' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the HtmlFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the HTML file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"HTML file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        """
        Extracts metadata from the HTML file, including text content, encoding, line count, 
        and word count.

        Raises:
            FileProcessingFailedError: If an error occurs during HTML file processing.
        """
        if not self.open_file:
            return

        logger.info(f"Starting processing of HTML file '{self.file_path}'.")
        try:
            encoding = chardet.detect(open(self.file_path, "rb").read())['encoding']
            logger.debug(f"Detected encoding '{encoding}' for HTML file '{self.file_path}'.")
            with open(self.file_path, 'r', encoding=encoding) as f:
                text = f.read()
                lines = text.split('\n')
                words = text.split()

            self.metadata.update({
                'text': text,
                'encoding': encoding,
                'lines': lines,
                'words': words,
                'num_lines': len(lines),
                'num_words': len(words),
            })
            logger.info(f"Successfully processed HTML file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process HTML file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the HTML file with updated metadata to the specified output path.

        Args:
            output_path (str): Path to save the processed HTML file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the HTML file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving HTML file '{self.file_path}' to '{save_path}'.")
        try:
            with open(save_path, 'w', encoding=self.metadata.get('encoding', 'utf-8')) as f:
                f.write(self.metadata['text'])
            logger.info(f"HTML file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save HTML file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving: {e}"
            )