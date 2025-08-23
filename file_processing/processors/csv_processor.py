import csv
import chardet
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

import logging
logger = logging.getLogger(__name__)

class CsvFileProcessor(FileProcessorStrategy):
    """
    Processor for handling CSV files, extracting metadata and saving processed data.

    Attributes:
        metadata (dict): Contains extracted metadata such as 'text', 'encoding', 'num_rows',
                         'num_cols', 'num_cells', and 'empty_cells' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the CsvFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the CSV file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with 'message' if `open_file` is False.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def process(self) -> None:
        """
        Extracts metadata from the CSV file if it is open and accessible.

        Metadata extracted includes the text content, encoding, number of rows, number of columns,
        total number of cells, and count of empty cells.

        Raises:
            FileProcessingFailedError: If an error occurs during CSV file processing.
        """
        logger.info(f"Starting processing of CSV file '{self.file_path}'.")
        if not self.open_file:
            logger.debug(f"CSV file '{self.file_path}' was not opened (open_file=False).")
            return
        try:
            raw_bytes = open(self.file_path, 'rb').read()
            encoding = chardet.detect(raw_bytes)['encoding'] or 'utf-8'
            logger.debug(f"Detected encoding '{encoding}' for CSV file '{self.file_path}'.")

            with open(self.file_path, 'r', newline='\n', encoding=encoding) as f:
                reader = csv.reader(f)
                rows = [row for row in reader]
                text = '\n'.join(['","'.join(row) for row in rows])

                num_cells = sum(len(row) for row in rows)
                empty_cells = sum(cell in ('', ' ') for row in rows for cell in row)

                logger.debug(f"Extracted {len(rows)} rows, "
                             f"{len(rows[0]) if rows else 0} columns, "
                             f"{num_cells} cells ({empty_cells} empty) from CSV file '{self.file_path}'.")

                self.metadata.update({
                    'text': text,
                    'encoding': encoding,
                    'num_rows': len(rows),
                    'num_cols': len(rows[0]) if rows else 0,
                    'num_cells': num_cells,
                    'empty_cells': empty_cells
                })
            logger.info(f"Successfully processed CSV file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process CSV file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the processed CSV file to the specified output path with updated metadata.

        Args:
            output_path (str): Path to save the processed CSV file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the CSV file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving CSV file '{self.file_path}' to '{save_path}'.")
        try:
            with open(save_path, 'w', newline='\n', encoding=self.metadata['encoding']) as f:
                writer = csv.writer(f)
                rows = self.metadata['text'].split('\n')
                for row in rows:
                    writer.writerow(row.split('","'))
            logger.info(f"CSV file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save CSV file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving file {self.file_path} to {save_path}: {e}"
            )