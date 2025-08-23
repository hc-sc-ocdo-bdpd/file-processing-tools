from striprtf.striprtf import rtf_to_text
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

import logging
logger = logging.getLogger(__name__)

class RtfFileProcessor(FileProcessorStrategy):
    """
    Processor for handling Rich Text Format (RTF) files, extracting plain text content.

    Attributes:
        metadata (dict): Contains metadata fields such as 'text' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the RtfFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the RTF file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"RTF file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        """
        Extracts text content from the RTF file and updates the metadata.

        Raises:
            FileProcessingFailedError: If an error occurs during RTF file processing.
        """
        if not self.open_file:
            logger.debug(f"RTF file '{self.file_path}' was not opened (open_file=False).")
            return

        logger.info(f"Starting processing of RTF file '{self.file_path}'.")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            self.metadata.update({"text": rtf_to_text(file_content)})
            logger.info(f"Successfully processed RTF file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process RTF file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves a copy of the RTF file to the specified output path.

        Args:
            output_path (str): Path to save the RTF file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the RTF file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving RTF file '{self.file_path}' to '{save_path}'.")
        try:
            with open(self.file_path, 'rb') as src_file:
                with open(save_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
            logger.info(f"RTF file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save RTF file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving {self.file_path}: {e}"
            )