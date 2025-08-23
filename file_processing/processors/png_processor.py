import logging
from PIL import Image
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class PngFileProcessor(FileProcessorStrategy):
    """
    Processor for handling PNG files, extracting metadata such as image format, mode,
    dimensions, and saving the file.

    Attributes:
        metadata (dict): Contains metadata fields such as 'original_format', 'mode', 'width',
                         and 'height' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the PngFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the PNG file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        if not open_file:
            self.metadata = {'message': 'File was not opened'}
            logger.debug(f"PNG file '{self.file_path}' was not opened (open_file=False).")
        else:
            self.metadata = {}

    def process(self) -> None:
        """
        Extracts metadata from the PNG file, including format, mode, width, and height.

        Raises:
            FileProcessingFailedError: If an error occurs while processing the PNG file.
        """
        logger.info(f"Starting processing of PNG file '{self.file_path}'.")

        if not self.open_file:
            logger.debug(f"PNG file '{self.file_path}' was not opened (open_file=False).")
            return

        try:
            image = Image.open(self.file_path)
            image.load()
            self.metadata.update({
                'original_format': image.format,
                'mode': image.mode,
                'width': image.width,
                'height': image.height,
            })
            logger.info(f"Successfully processed PNG file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process PNG file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the PNG file to the specified output path.

        Args:
            output_path (str): Path to save the PNG file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the PNG file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving PNG file '{self.file_path}' to '{save_path}'.")

        try:
            image = Image.open(self.file_path)
            image.save(save_path)
            logger.info(f"PNG file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save PNG file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving to {save_path}: {e}"
            )