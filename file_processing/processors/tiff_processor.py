from PIL import Image
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

import logging
logger = logging.getLogger(__name__)

class TiffFileProcessor(FileProcessorStrategy):
    """
    Processor for handling TIFF (Tagged Image File Format) files, extracting metadata
    such as image format, mode, dimensions, and saving the file.

    Attributes:
        metadata (dict): Contains metadata fields such as 'original_format', 'mode', 'width',
                         and 'height' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the TiffFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the TIFF file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"TIFF file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        """
        Extracts metadata from the TIFF file, including format, mode, width, and height.

        Raises:
            FileProcessingFailedError: If an error occurs while processing the TIFF file.
        """
        if not self.open_file:
            logger.debug(f"TIFF file '{self.file_path}' was not opened (open_file=False).")
            return

        logger.info(f"Starting processing of TIFF file '{self.file_path}'.")
        try:
            image = Image.open(self.file_path)
            image.load()
            self.metadata.update({
                'original_format': image.format,
                'mode': image.mode,
                'width': image.width,
                'height': image.height,
            })
            logger.info(f"Successfully processed TIFF file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process TIFF file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the TIFF file to the specified output path.

        Args:
            output_path (str): Path to save the TIFF file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the TIFF file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving TIFF file '{self.file_path}' to '{save_path}'.")
        try:
            image = Image.open(self.file_path)
            image.save(save_path)
            logger.info(f"TIFF file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save TIFF file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving to {save_path}: {e}"
            )