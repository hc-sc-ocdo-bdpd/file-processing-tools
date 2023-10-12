from file_processor_strategy import FileProcessorStrategy
from PIL import Image

class JpegFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.metadata = {}

    def process(self) -> None:
        image = Image.open(self.file_path)
        image.load()
        self.metadata.update({
            'original_format': image.format,
            # mode defines type and width of a pixel (https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes)
            'mode': image.mode,
            'width': image.width,
            'height': image.height,
        })

    def save(self, output_path: str = None) -> None:
        image = Image.open(self.file_path)
        
        save_path = output_path or self.file_path
        image.save(save_path)
    
    def save_as_pdf(self, output_path: str) -> None:
        image = Image.open(self.file_path)

        image.save(output_path, "PDF", resolution=100)