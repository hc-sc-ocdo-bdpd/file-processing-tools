import chardet
import re
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

import logging
logger = logging.getLogger(__name__)

class CppFileProcessor(FileProcessorStrategy):
    """
    Processor for handling C++ source files (.cpp, .cc), extracting metadata and content.

    Attributes:
        metadata (dict): Contains metadata such as 'text', 'encoding', 'num_lines',
                         'num_functions', 'num_classes', and 'num_comments'.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def process(self) -> None:
        logger.info(f"Starting processing of C++ file '{self.file_path}'.")
        if not self.open_file:
            logger.debug(f"C++ file '{self.file_path}' was not opened (open_file=False).")
            return
        try:
            raw_data = open(self.file_path, 'rb').read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            logger.debug(f"Detected encoding '{encoding}' for C++ file '{self.file_path}'.")

            with open(self.file_path, 'r', encoding=encoding, errors='replace') as f:
                text = f.read()
                num_lines = len(text.splitlines())
                num_functions = len(re.findall(r'\b[a-zA-Z_]\w*\s+[a-zA-Z_]\w*\s*\(.*?\)\s*\{', text))
                num_classes = len(re.findall(r'\bclass\s+\w+', text))
                num_comments = len(re.findall(r'(//[^\n]*|/\*.*?\*/)', text, re.DOTALL))

                logger.debug(f"Extracted {num_lines} lines, {num_functions} functions, "
                             f"{num_classes} classes, and {num_comments} comments from C++ file '{self.file_path}'.")

                self.metadata.update({
                    'text': text,
                    'encoding': encoding,
                    'num_lines': num_lines,
                    'num_functions': num_functions,
                    'num_classes': num_classes,
                    'num_comments': num_comments
                })

            logger.info(f"Successfully processed C++ file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process C++ file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        save_path = output_path or self.file_path
        logger.info(f"Saving C++ file '{self.file_path}' to '{save_path}'.")
        try:
            with open(save_path, 'w', encoding=self.metadata['encoding']) as f:
                f.write(self.metadata['text'])
            logger.info(f"C++ file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save C++ file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error saving {self.file_path} to {save_path}: {e}"
            )
