from PIL import Image
from .file_processor_strategy import FileProcessorStrategy
from .errors import FileProcessingFailedError

class PngFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}

    def process(self) -> None:
        if not self.open_file:
            return

        try:
            image = Image.open(self.file_path)
            image.load()
            self.metadata.update({
                'original_format': image.format,
                # mode defines type and width of a pixel (https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes)
                'mode': image.mode,
                'width': image.width,
                'height': image.height,
            })
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing {self.file_path}: {e}")
    
    
    def save(self, output_path: str = None) -> None:
        try:
            image = Image.open(self.file_path)
            
            save_path = output_path or self.file_path
            image.save(save_path)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving to {save_path}: {e}")