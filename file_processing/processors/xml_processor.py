import chardet
import logging
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class XmlFileProcessor(FileProcessorStrategy):
    """
    Processor for handling XML files, extracting metadata such as encoding, text content,
    line count, word count, and individual lines and words.

    Attributes:
        metadata (dict): Contains metadata fields such as 'text', 'encoding', 'lines', 'words',
                         'num_lines', and 'num_words' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the XmlFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the XML file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def process(self) -> None:
        """
        Extracts metadata from the XML file, including encoding, text content, line count,
        word count, individual lines, and words.

        Raises:
            FileProcessingFailedError: If an error occurs while processing the XML file.
        """
        if not self.open_file:
            logger.debug(f"XML file '{self.file_path}' was not opened (open_file=False).")
            return

        logger.info(f"Starting processing of XML file '{self.file_path}'.")

        try:
            raw_data = open(self.file_path, "rb").read()
            encoding = chardet.detect(raw_data)['encoding']
            logger.debug(f"Detected encoding '{encoding}' for XML file '{self.file_path}'.")
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

            logger.info(f"Successfully processed XML file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process XML file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the XML file with the extracted metadata to the specified output path.

        Args:
            output_path (str): Path to save the XML file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the XML file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving XML file '{self.file_path}' to '{save_path}'.")

        try:
            with open(save_path, 'w', encoding=self.metadata['encoding']) as f:
                f.write(self.metadata['text'])
            logger.info(f"XML file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save XML file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving {self.file_path}: {e}"
            )