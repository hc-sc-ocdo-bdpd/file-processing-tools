import chardet
import re
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy
import logging

logger = logging.getLogger(__name__)

class GoFileProcessor(FileProcessorStrategy):
    """
    Processor for handling Go source files (.go), extracting metadata and content.

    Attributes:
        metadata (dict): Contains metadata such as 'text', 'encoding', 'num_lines',
                         'num_functions', 'num_structs', and 'num_interfaces'.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        if not open_file:
            self.metadata = {'message': 'File was not opened'}
            logger.debug(f"Go file '{self.file_path}' was not opened (open_file=False).")
        else:
            self.metadata = {}

    def process(self) -> None:
        logger.info(f"Starting processing of Go file '{self.file_path}'.")
        if not self.open_file:
            logger.debug(f"Go file '{self.file_path}' was not opened (open_file=False).")
            return
        try:
            raw_data = open(self.file_path, 'rb').read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            logger.debug(f"Detected encoding '{encoding}' for Go file '{self.file_path}'.")

            with open(self.file_path, 'r', encoding=encoding) as f:
                text = f.read()

            num_lines = len(text.splitlines())
            num_functions = len(re.findall(r'\bfunc\s+\w+\s*\(', text))
            num_structs = len(re.findall(r'\btype\s+\w+\s+struct\s*\{', text))
            num_interfaces = len(re.findall(r'\btype\s+\w+\s+interface\s*\{', text))

            self.metadata.update({
                'text': text,
                'encoding': encoding,
                'num_lines': num_lines,
                'num_functions': num_functions,
                'num_structs': num_structs,
                'num_interfaces': num_interfaces
            })

            logger.info(f"Successfully processed Go file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process Go file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        save_path = output_path or self.file_path
        logger.info(f"Saving Go file '{self.file_path}' to '{save_path}'.")
        try:
            with open(save_path, 'w', encoding=self.metadata['encoding']) as f:
                f.write(self.metadata['text'])
            logger.info(f"Go file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save Go file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error saving {self.file_path} to {save_path}: {e}"
            )