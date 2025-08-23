import json
from json.decoder import JSONDecodeError
import chardet
import logging
from file_processing.file_processor_strategy import FileProcessorStrategy
from file_processing.errors import FileProcessingFailedError, FileCorruptionError

logger = logging.getLogger(__name__)

class JsonFileProcessor(FileProcessorStrategy):
    """
    Processor for handling JSON files, extracting metadata such as encoding, key names, and
    counting keys and empty values.

    Attributes:
        metadata (dict): Contains metadata fields such as 'text', 'encoding', 'num_keys',
                         'key_names', and 'empty_values' if the file is opened.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the JsonFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the JSON file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized as empty.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
        if not open_file:
            logger.debug(f"JSON file '{self.file_path}' was not opened (open_file=False).")

    def process(self) -> None:
        """
        Extracts metadata from the JSON file, including encoding, text content, number of keys,
        key names, and count of empty values.

        Raises:
            FileCorruptionError: If the file is corrupted and cannot be parsed as JSON.
            FileProcessingFailedError: If an error occurs during JSON file processing.
        """
        if not self.open_file:
            return

        logger.info(f"Starting processing of JSON file '{self.file_path}'.")
        try:
            with open(self.file_path, 'rb') as f:
                binary_content = f.read()

            encoding = chardet.detect(binary_content)['encoding']
            logger.debug(f"Detected encoding '{encoding}' for JSON file '{self.file_path}'.")

            content = binary_content.decode(encoding)
            data = json.loads(content)
            text = json.dumps(data)
            num_keys = self.count_keys(data)
            empty_values = self.count_empty_values(data)
            key_names = self.get_key_names(data)

            self.metadata.update({
                'text': text,
                'encoding': encoding,
                'num_keys': num_keys,
                'key_names': key_names,
                'empty_values': empty_values,
            })

            logger.info(f"Successfully processed JSON file '{self.file_path}'.")
        except JSONDecodeError as e:
            logger.error(f"Failed to process JSON file '{self.file_path}': {e}")
            raise FileCorruptionError(f"File is corrupted: {self.file_path}") from e
        except Exception as e:
            logger.error(f"Failed to process JSON file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def count_empty_values(self, data: dict) -> int:
        empty_values = 0
        for key in data.keys():
            if data[key] == '':
                empty_values += 1
            elif isinstance(data[key], dict):
                empty_values += self.count_empty_values(data[key])
        return empty_values

    def count_keys(self, data: dict) -> int:
        num_keys = len(data.keys())
        for key in data.keys():
            if isinstance(data[key], dict):
                num_keys += self.count_keys(data[key])
        return num_keys

    def get_key_names(self, data: dict) -> list:
        key_names = []
        for key in data.keys():
            key_names.append(key)
            if isinstance(data[key], dict):
                key_names += self.get_key_names(data[key])
        return key_names

    def save(self, output_path: str = None) -> None:
        """
        Saves the JSON file with updated metadata to the specified output path.

        Args:
            output_path (str): Path to save the processed JSON file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the JSON file.
        """
        save_path = output_path or self.file_path
        logger.info(f"Saving JSON file '{self.file_path}' to '{save_path}'.")
        try:
            with open(save_path, 'w', encoding=self.metadata['encoding']) as f:
                json.dump(json.loads(self.metadata['text']), f, indent=4)
            logger.info(f"JSON file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save JSON file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving file {self.file_path} to {save_path}: {e}"
            )
