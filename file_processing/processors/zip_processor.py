import logging
from pathlib import Path
import shutil
import zipfile
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class ZipFileProcessor(FileProcessorStrategy):
    """
    Processor for handling ZIP archive files, extracting metadata such as the number of files,
    file types, and file names within the archive.

    Attributes:
        metadata (dict): Contains metadata fields such as 'num_files', 'file_types', and 'file_names'
                         if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the ZipFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the ZIP file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"ZIP file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        """
        Extracts metadata from the ZIP file, including the number of files, file types,
        and file names.

        Raises:
            FileProcessingFailedError: If an error occurs while processing the ZIP file.
        """
        if not self.open_file:
            logger.debug(f"ZIP file '{self.file_path}' was not opened (open_file=False).")
            return

        logger.info(f"Starting processing of ZIP file '{self.file_path}'.")
        try:
            z = zipfile.ZipFile(self.file_path, 'r')
            self.metadata.update({
                "num_files": len(z.infolist()),
                "file_types": self.extract_file_types(z),
                "file_names": z.namelist()
            })
            logger.info(f"Successfully processed ZIP file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process ZIP file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    @staticmethod
    def extract_file_types(z):
        """
        Extracts the file types and their counts from the ZIP file.

        Args:
            z (ZipFile): An open ZipFile instance.

        Returns:
            dict: Dictionary with file extensions as keys and their counts as values.

        Raises:
            FileProcessingFailedError: If an error occurs while extracting file types.
        """
        try:
            types = {}
            for info in z.infolist():
                fname = info.filename
                ext = fname[fname.find('.') + 1:]
                types[ext] = types.get(ext, 0) + 1
            return types
        except Exception as e:
            raise FileProcessingFailedError(
                f"Error encountered while extracting file types: {e}"
            )

    def extract(self, output_dir: str = None) -> None:
        """
        Extracts the contents of the ZIP file to the specified directory.

        Args:
            output_dir (str): Directory to extract the ZIP contents. If None, creates a directory
                              with the same name as the ZIP file.

        Raises:
            FileProcessingFailedError: If an error occurs while extracting the ZIP file.
        """
        try:
            if not output_dir:
                output_dir = self.file_path.with_suffix('')

            Path(output_dir).mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
        except Exception as e:
            raise FileProcessingFailedError(
                f"Error encountered while extracting {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the ZIP file to the specified output path.

        Args:
            output_path (str): Path to save the ZIP file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the ZIP file.
        """
        save_path = output_path or str(self.file_path)
        logger.info(f"Saving ZIP file '{self.file_path}' to '{save_path}'.")
        try:
            shutil.copy2(self.file_path, save_path)
            logger.info(f"ZIP file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save ZIP file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving {self.file_path}: {e}"
            )