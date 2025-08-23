import chardet
import re
import logging
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class HFileProcessor(FileProcessorStrategy):
    """
    Processor for handling C/C++ header files (.h), extracting metadata and content.

    Attributes:
        metadata (dict): Contains metadata such as:
            'text' (str): Full file content as string.
            'encoding' (str): Detected file encoding.
            'num_lines' (int): Total number of lines.
            'num_includes' (int): Count of preprocessor #include statements.
            'num_macros' (int): Count of #define statements.
            'num_structs' (int): Count of struct definitions.
            'num_classes' (int): Count of class definitions (common in C++ headers).
            'num_comments' (int): Count of single-line and multi-line comments.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"H file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        if not self.open_file:
            return
        logger.info(f"Starting processing of H file '{self.file_path}'.")
        try:
            raw_data = open(self.file_path, 'rb').read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            logger.debug(f"Detected encoding '{encoding}' for H file '{self.file_path}'.")

            with open(self.file_path, 'r', encoding=encoding, errors='replace') as f:
                text = f.read()

            num_lines = len(text.splitlines())

            include_pattern = re.compile(r'^\s*#\s*include\s+["<].*[">]', re.MULTILINE)
            macro_pattern = re.compile(r'^\s*#\s*define\s+\w+', re.MULTILINE)
            struct_pattern = re.compile(r'\bstruct\s+\w+', re.MULTILINE)
            class_pattern = re.compile(r'\bclass\s+\w+', re.MULTILINE)
            comment_pattern = re.compile(r'(//[^\n]*|/\*.*?\*/)', re.DOTALL)

            num_includes = len(include_pattern.findall(text))
            num_macros = len(macro_pattern.findall(text))
            num_structs = len(struct_pattern.findall(text))
            num_classes = len(class_pattern.findall(text))
            num_comments = len(comment_pattern.findall(text))

            self.metadata.update({
                'text': text,
                'encoding': encoding,
                'num_lines': num_lines,
                'num_includes': num_includes,
                'num_macros': num_macros,
                'num_structs': num_structs,
                'num_classes': num_classes,
                'num_comments': num_comments,
            })

            logger.info(f"Successfully processed H file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process H file '{self.file_path}': {e}")
            raise FileProcessingFailedError(f"Error processing {self.file_path}: {e}")

    def save(self, output_path: str = None) -> None:
        save_path = output_path or self.file_path
        logger.info(f"Saving H file '{self.file_path}' to '{save_path}'.")
        try:
            with open(save_path, 'w', encoding=self.metadata['encoding']) as f:
                f.write(self.metadata['text'])
            logger.info(f"H file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save H file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(f"Error saving {self.file_path} to {save_path}: {e}")