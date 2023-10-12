from file_processor_strategy import FileProcessorStrategy
import chardet

#Specialized python library for pulling html/xml data...
#https://beautiful-soup-4.readthedocs.io/en/latest/

class HtmlFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.metadata = {}

    def process(self) -> None:
        # Reads the file and updates the metadata with information about the file
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

    def save(self, output_path: str = None) -> None:
        save_path = output_path or self.file_path
        with open(save_path, 'w', encoding = self.metadata['encoding']) as f:
            f.write(self.metadata['text'])
    
    def save_as_txt(self, output_path: str = None) -> None:
        save_path = output_path or self.file_path
        with open(save_path, 'w', encoding = self.metadata['encoding']) as f:
            f.write(self.metadata['text'])