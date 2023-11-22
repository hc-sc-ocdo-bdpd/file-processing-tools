import extract_msg
from .file_processor_strategy import FileProcessorStrategy
from .errors import FileProcessingFailedError

class MsgFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
    
    def process(self) -> None:
        if not self.open_file:
            return

        try:
            msg = extract_msg.Message(self.file_path)
            self.metadata.update({'text': msg.body})
            self.metadata.update({'subject': msg.subject})
            self.metadata.update({'date': msg.date})
            self.metadata.update({'sender': msg.sender})
            msg.close()
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing: {e}")




    def save(self, output_path: str = None) -> None:
        try:
            output_path = output_path or self.file_path
            msg_file = extract_msg.Message(self.file_path)
            msg_file.export(path=output_path)
            msg_file.close()
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving: {e}")
    