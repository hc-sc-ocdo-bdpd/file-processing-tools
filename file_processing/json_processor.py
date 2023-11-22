import json
import chardet
from json.decoder import JSONDecodeError
from .file_processor_strategy import FileProcessorStrategy
from .errors import FileProcessingFailedError, FileCorruptionError

class JsonFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def process(self) -> None:
        if not self.open_file:
            return

        try:
            with open(self.file_path, 'rb') as f:
                binary_content = f.read()
            
            encoding = chardet.detect(binary_content)['encoding']
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
        except JSONDecodeError as e:
            raise FileCorruptionError(f"File is corrupted: {self.file_path}")
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing {self.file_path}: {e}")

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
        save_path = output_path or self.file_path
        try:
            with open(save_path, 'w', encoding = self.metadata['encoding']) as f:
                json.dump(json.loads(self.metadata['text']), f, indent=4)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving file {self.file_path} to {save_path}: {e}")