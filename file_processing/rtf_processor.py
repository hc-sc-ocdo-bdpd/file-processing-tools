from file_processor_strategy import FileProcessorStrategy
from striprtf.striprtf import rtf_to_text
from errors import FileProcessingFailedError, UnsupportedFileTypeError

class RtfFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def process(self) -> None:
        if not self.open_file:
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            self.metadata.update({"text": rtf_to_text(file_content)})
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing {self.file_path}: {e}")


    def save(self, output_path: str = None) -> None:
        try:
            with open(self.file_path, 'rb') as src_file:
                with open(output_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving {self.file_path}: {e}")