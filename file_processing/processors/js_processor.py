import chardet
import re
import logging
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class JsFileProcessor(FileProcessorStrategy):
    """
    Processor for handling JavaScript (.js) source files, extracting metadata and content.

    Attributes:
        metadata (dict): Contains metadata such as 'text', 'encoding', 'num_lines',
                         'num_functions', 'num_classes', and 'num_comments'.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"JavaScript file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        """Extracts JavaScript file metadata if open_file is True."""
        if not self.open_file:
            return

        logger.info(f"Starting processing of JavaScript file '{self.file_path}'.")
        try:
            raw_data = open(self.file_path, 'rb').read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            logger.debug(f"Detected encoding '{encoding}' for JavaScript file '{self.file_path}'.")

            with open(self.file_path, 'r', encoding=encoding, errors='replace') as f:
                text = f.read()

            num_lines = len(text.splitlines())

            function_pattern = re.compile(r'\b(function|export\s+function)\s+[A-Za-z_]\w*\s*\(.*?\)\s*\{')
            class_pattern = re.compile(r'\bclass\s+[A-Za-z_]\w*\s*\{?')
            comment_pattern = re.compile(r'(//[^\n]*|/\*.*?\*/)', re.DOTALL)

            num_functions = len(function_pattern.findall(text))
            num_classes = len(class_pattern.findall(text))
            num_comments = len(comment_pattern.findall(text))

            self.metadata.update({
                'text': text,
                'encoding': encoding,
                'num_lines': num_lines,
                'num_functions': num_functions,
                'num_classes': num_classes,
                'num_comments': num_comments
            })

            logger.info(f"Successfully processed JavaScript file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process JavaScript file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """Saves the JavaScript file to the specified path."""
        save_path = output_path or self.file_path
        logger.info(f"Saving JavaScript file '{self.file_path}' to '{save_path}'.")
        try:
            with open(save_path, 'w', encoding=self.metadata['encoding']) as f:
                f.write(self.metadata['text'])
            logger.info(f"JavaScript file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save JavaScript file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error saving {self.file_path} to {save_path}: {e}"
            )