import json
import logging
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class IpynbFileProcessor(FileProcessorStrategy):
    """
    Processor for handling Jupyter Notebook (.ipynb) files, extracting text content and metadata.

    Attributes:
        metadata (dict): Contains metadata fields such as 'text', 'num_cells', 'num_code_cells',
                         and 'num_markdown_cells' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the IpynbFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the .ipynb file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"IPYNB file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        """
        Extracts metadata from the .ipynb file, including text content, number of cells,
        number of code cells, and number of markdown cells.

        Raises:
            FileProcessingFailedError: If an error occurs during .ipynb file processing.
        """
        if not self.open_file:
            return

        logger.info(f"Starting processing of IPYNB file '{self.file_path}'.")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            cells = notebook.get('cells', [])
            text = []
            for cell in cells:
                if cell['cell_type'] in ['markdown', 'code']:
                    text.append(' '.join(cell['source']).replace('\n', ' ') + '\n')

            self.metadata.update({
                'text': ''.join(text),
                'num_cells': len(cells),
                'num_code_cells': sum(1 for cell in cells if cell['cell_type'] == 'code'),
                'num_markdown_cells': sum(1 for cell in cells if cell['cell_type'] == 'markdown')
            })
            logger.info(f"Successfully processed IPYNB file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process IPYNB file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def save(self, output_path: str = None) -> None:
        """
        Saves the .ipynb file with updated metadata to the specified output path.

        Args:
            output_path (str): Path to save the processed .ipynb file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the .ipynb file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving IPYNB file '{self.file_path}' to '{save_path}'.")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            text = self.metadata.get('text', '').split('\n')
            idx = 0
            for cell in notebook.get('cells', []):
                if cell['cell_type'] in ['markdown', 'code']:
                    cell['source'] = text[idx].split(' ')
                    idx += 1

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=4)
            logger.info(f"IPYNB file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save IPYNB file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving file {self.file_path} to {save_path}: {e}"
            )