import shutil
from .file_processor_strategy import FileProcessorStrategy

class GenericFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path)
        self.metadata = {
            'message': 'This is a generic processor. Limited functionality available. File was not opened'
        }

    def process(self) -> None:
        pass

    def save(self, output_path: str = None) -> None:
        if output_path:
            shutil.copy2(self.file_path, output_path)
        else:
            print("No output path provided, file not saved.")