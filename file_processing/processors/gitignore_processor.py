import chardet
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy
import logging

logger = logging.getLogger(__name__)

class GitignoreFileProcessor(FileProcessorStrategy):
    """
    Processor for handling .gitignore files, extracting metadata such as text content, encoding,
    line count, and word count.

    Attributes:
        metadata (dict): Contains metadata fields such as 'text', 'encoding', 'lines', 'words',
                         'num_lines', and 'num_words' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the GitignoreFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the .gitignore file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False.
        """
        super().__init__(file_path, open_file)
        if not open_file:
            self.metadata = {'message': 'File was not opened'}
            logger.debug(f"Gitignore file '{self.file_path}' was not opened (open_file=False).")
        else:
            self.metadata = {}

    def process(self) -> None:
        """
        Extracts metadata from the .gitignore file, including text content, encoding, lines, words,
        line count, and word count.

        Raises:
            FileProcessingFailedError: If an error occurs during .gitignore file processing.
            UnicodeDecodeError: If there is a decoding error when reading the file.
        """
        logger.info(f"Starting processing of Gitignore file '{self.file_path}'.")
        if not self.open_file:
            logger.debug(f"Gitignore file '{self.file_path}' was not opened (open_file=False).")
            return

        try:
            with open(self.file_path, "rb") as f:
                encoding = chardet.detect(f.read())['encoding']
                logger.debug(f"Detected encoding '{encoding}' for Gitignore file '{self.file_path}'.")

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
            logger.info(f"Successfully processed Gitignore file '{self.file_path}'.")
        except UnicodeDecodeError as ude:
            logger.error(f"Failed to process Gitignore file '{self.file_path}': {ude}")
            raise FileProcessingFailedError(
                f"Unicode decoding error encountered while processing {self.file_path}: {ude}"
            )
        except Exception as e:
            logger.error(f"Failed to process Gitignore file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the .gitignore file to the specified output path with updated metadata.

        Args:
            output_path (str): Path to save the file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the .gitignore file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving Gitignore file '{self.file_path}' to '{save_path}'.")
        try:
            encoding = self.metadata.get('encoding', 'utf-8')
            with open(save_path, 'w', encoding=encoding) as f:
                f.write(self.metadata['text'])
            logger.info(f"Gitignore file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save Gitignore file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving {self.file_path}: {e}"
            )