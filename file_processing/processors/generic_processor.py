import shutil
import logging
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class GenericFileProcessor(FileProcessorStrategy):
    """
    Generic processor for handling unsupported or unrecognized file types.
    Provides minimal functionality, primarily copying files as-is.

    Attributes:
        metadata (dict): Contains a message indicating limited functionality.
        parent_directory (Path): The directory containing the file.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the GenericFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the file to process.
            open_file (bool): Indicates whether to open and process the file. Default is False.
        
        Sets:
            metadata (dict): Contains a message noting limited functionality.
            parent_directory (Path): Set to the file's parent directory.
        """
        super().__init__(file_path)
        self.metadata = {'message': 'This is a generic processor. Limited functionality available. File was not opened'}
        self.parent_directory = self.file_path.parent  # Add parent_directory

    def process(self) -> None:
        """
        Process method for unsupported file types. Does nothing as it serves as a placeholder
        for unsupported files, providing only minimal functionality.
        """
        logger.info(f"Processing skipped for unsupported file type '{self.file_path}' using GenericFileProcessor.")

    def save(self, output_path: str = None) -> None:
        """
        Saves a copy of the file to the specified output path if provided.

        Args:
            output_path (str): Path to save the file. If None, logs a message and does not save.

        Raises:
            FileProcessingFailedError: If an error occurs during the file save operation.
        """
        if output_path:
            logger.info(f"Saving generic file '{self.file_path}' to '{output_path}'.")
            try:
                shutil.copy2(self.file_path, output_path)
                logger.info(f"Generic file '{self.file_path}' saved successfully to '{output_path}'.")
            except Exception as e:
                logger.error(f"Failed to save generic file '{self.file_path}' to '{output_path}': {e}")
                raise FileProcessingFailedError(f"Error encountered while saving {self.file_path}: {e}")
        else:
            logger.info(f"No output path provided, generic file '{self.file_path}' was not saved.")