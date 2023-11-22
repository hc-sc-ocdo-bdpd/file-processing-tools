import chardet
from .file_processor_strategy import FileProcessorStrategy
from .errors import FileProcessingFailedError

#Specialized python library for pulling html/xml data...
#https://beautiful-soup-4.readthedocs.io/en/latest/

class HtmlFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def process(self) -> None:
        if not self.open_file:
            return

        try:
            encoding = chardet.detect(open(self.file_path, "rb").read())['encoding']
            with open(self.file_path, 'r', encoding=encoding) as f:
                text = f.read()
                lines = text.split('\n')
                words = text.split()

            self.metadata.update({
                'text': text,
                'encoding': encoding,
                'lines': lines,
                'words': words,
                'num_lines': len(lines),
                'num_words': len(words),
            })
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing: {e}")


    def save(self, output_path: str = None) -> None:
        try:
            save_path = output_path or self.file_path
            with open(save_path, 'w', encoding = self.metadata['encoding']) as f:
                f.write(self.metadata['text'])
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving: {e}")