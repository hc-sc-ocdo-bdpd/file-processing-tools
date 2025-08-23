import chardet
import re
import logging
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class RbFileProcessor(FileProcessorStrategy):
    """
    Processor for handling Ruby (.rb) source files, extracting metadata and content.

    Attributes:
        metadata (dict): Contains metadata such as 'text', 'encoding', 'num_lines',
                         'num_methods', 'num_classes', and 'num_modules'.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        if not open_file:
            logger.debug(f"RB file '{self.file_path}' was not opened (open_file=False).")
            self.metadata = {'message': 'File was not opened'}
        else:
            self.metadata = {}

    def process(self) -> None:
        logger.info(f"Starting processing of RB file '{self.file_path}'.")

        if not self.open_file:
            return
        try:
            raw_data = open(self.file_path, 'rb').read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            logger.debug(f"Detected encoding '{encoding}' for RB file '{self.file_path}'.")

            with open(self.file_path, 'r', encoding=encoding) as f:
                text = f.read()

            num_lines = len(text.splitlines())
            num_methods = len(re.findall(r'^\s*def\s+\w+', text, re.MULTILINE))
            num_classes = len(re.findall(r'^\s*class\s+\w+', text, re.MULTILINE))
            num_modules = len(re.findall(r'^\s*module\s+\w+', text, re.MULTILINE))

            self.metadata.update({
                'text': text,
                'encoding': encoding,
                'num_lines': num_lines,
                'num_methods': num_methods,
                'num_classes': num_classes,
                'num_modules': num_modules
            })

            logger.info(f"Successfully processed RB file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process RB file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        save_path = output_path or self.file_path
        logger.info(f"Saving RB file '{self.file_path}' to '{save_path}'.")

        try:
            with open(save_path, 'w', encoding=self.metadata['encoding']) as f:
                f.write(self.metadata['text'])
            logger.info(f"RB file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save RB file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error saving {self.file_path} to {save_path}: {e}"
            )