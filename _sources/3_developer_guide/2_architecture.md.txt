<br>

# Architecture and Design Patterns

The strategy design pattern is used:

1. **Main File** (`file.py`): Determines the file type based on its extension and delegates the processing to the appropriate processor.
2. **Strategy Base** (`file_processor_strategy.py`): An abstract base class that sets the foundation for all file processors.
3. **Specific File Processors** (like `docx_processor.py`, `pdf_processor.py`, `txt_processor.py`): Handle the unique processing for each file type. They inherit from the base strategy and implement the `process` method.

```{tab} File
This is the `File` object that detects the file extension and abstracts processing to the appropriate processor defined in the `PROCESSORS` dictionary.

```python
PROCESSORS = {
        ".csv": processors.CsvFileProcessor,
        ".txt": processors.TextFileProcessor,
        ".pdf": processors.PdfFileProcessor,
        ...
}
...
def _get_processor(self, use_ocr: bool, use_transcriber: bool, open_file: bool) -> FileProcessorStrategy:
    extension = self.path.suffix
    processor_class = File.PROCESSORS.get(extension, processors.GenericFileProcessor)
    processor = processor_class(str(self.path), open_file)
```
```{tab} FileProcessorStrategy
This is the base class that is inherited by each specific processor. It assigns values to the `File` object's properties in the `__init__` function, then defines the abstract methods that will be overwritten.

```python
class FileProcessorStrategy(ABC):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        self.file_path = Path(file_path)
        self.open_file = open_file
        self.file_name = self.file_path.name
        ...

    @abstractmethod
    def process(self) -> None:
        # Abstract method to be implemented by subclasses for file processing
        if not self.open_file:
            return

    @abstractmethod
    def save(self) -> None:
        """Saves the processed file after metadata changes"""

```
```{tab} GenericProcessor
These file-specific processors will overwrite the `process` and `save` abstract methods of the `FileProcessorStrategy` base class.

```python
class GenericFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path)
        self.metadata = {'message': 'This is a generic processor. Limited functionality available. File was not opened'}

    def process(self) -> None:
        pass

    def save(self, output_path: str = None) -> None:
        if output_path:
            shutil.copy2(self.file_path, output_path)
        else:
            logging.info("No output path provided, file not saved.")
```
