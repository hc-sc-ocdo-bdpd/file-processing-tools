# file-processing

A versatile Python library for generalizing and streamlining the processing of diverse file types. It provides a unified `File` class that uses the Strategy Pattern to select appropriate processors based on file extensions. The library supports over 20 unique file processors and is designed for easy extensibility.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported File Types](#supported-file-types)
- [Optional Features](#optional-features)
- [Architecture](#architecture)
- [Extending the Library](#extending-the-library)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **Unified File Interface**: Interact with different file types using a single `File` class.
- **Strategy Pattern Implementation**: Dynamically selects the appropriate processor based on file extensions.
- **Extensible Design**: Easily add support for new file types by creating custom processors.
- **Metadata Extraction**: Extracts comprehensive metadata and text content from files.
- **Lazy Loading for Optional Features**: Supports optional OCR and transcription capabilities via `file-processing-ocr` and `file-processing-transcription`.

---

## Installation

To install the `file-processing` library from GitHub (since it's not packaged yet), use pip with the repository URL:

```bash
pip install git+https://github.com/hc-sc-ocdo-bdpd/file-processing.git
```

*Note*: Optional dependencies for OCR and transcription are available through `file-processing-ocr` and `file-processing-transcription`.

---

## Quick Start

Here's how to get started with `file-processing`:

```python
from file_processing import File

# Initialize a File object
file = File('path/to/your/file.pdf')

# Access metadata
print(f"File Name: {file.file_name}")
print(f"File Size: {file.size} bytes")
print(f"Owner: {file.owner}")

# Access extracted text (if applicable)
print(f"Text Content: {file.metadata.get('text', 'No text extracted')}")
```

---

## Supported File Types

The library supports a wide range of file types:

- **Text-Based Files**: `.txt`, `.csv`, `.json`, `.xml`, `.html`, `.py`, `.ipynb`, `.gitignore`
- **Documents**: `.pdf`, `.docx`, `.rtf`, `.xlsx`, `.pptx`, `.msg`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.tif`, `.tiff`, `.heic`, `.heif`
- **Audio/Video Files**: `.mp3`, `.wav`, `.mp4`, `.flac`, `.aiff`, `.ogg`
- **Archives**: `.zip`
- **Packaged Software**: `.whl`, `.exe`
- **Model Files**: `.gguf` (used with `file-processing-models`)

---

## Optional Features

The `file-processing` library can be extended with OCR and transcription capabilities by installing additional packages:

- **OCR**: [file-processing-ocr](https://github.com/hc-sc-ocdo-bdpd/file-processing-ocr)
- **Transcription**: [file-processing-transcription](https://github.com/hc-sc-ocdo-bdpd/file-processing-transcription)

---

## Architecture

The library utilizes the **Strategy Pattern** to select the appropriate processor based on the file extension. Here's how it works:

- The `File` class acts as a context that delegates the processing to a specific `FileProcessorStrategy`.
- Each file type has a corresponding processor class that implements the `FileProcessorStrategy` interface.
- If a file type is not explicitly supported, a `GenericFileProcessor` is used as a fallback.

---

## Extending the Library

To add support for a new file type:

1. **Create a New Processor Class**:

   ```python
   from file_processing.file_processor_strategy import FileProcessorStrategy

   class CustomFileProcessor(FileProcessorStrategy):
       def __init__(self, file_path: str, open_file: bool = True) -> None:
           super().__init__(file_path, open_file)
           self.metadata = {}

       def process(self) -> None:
           # Implement processing logic
           pass

       def save(self, output_path: str = None) -> None:
           # Implement save logic
           pass
   ```

2. **Register the New Processor in `file.py`**:

   Add your new processor to the `PROCESSORS` dictionary in `file_processing/file.py`:

   ```python
   File.PROCESSORS['.custom_extension'] = CustomFileProcessor
   ```

3. **Update the `__init__.py` File**:

   Add an import statement for your new processor in `file_processing/processors/__init__.py`:

   ```python
   from .custom_processor import CustomFileProcessor
   ```

Following these steps ensures your new processor is correctly integrated with the `file-processing` library.

---

## Logging  
  
The `file-processing` library uses Python's built-in `logging` module. By default, it does not configure logging to avoid interfering with your application's logging setup.   
  
To enable our recommended logging configuration, explicitly call:  
  
```python  
from file_processing.logging_setup import setup_logging  
setup_logging()  

---

## Contributing

We welcome contributions from the community. If you'd like to contribute:

- **Fork the Repository**: Create your own fork on GitHub.
- **Create a Feature Branch**: Work on your feature or bug fix in a separate branch.
- **Write Tests**: Ensure your changes are covered by tests.
- **Submit a Pull Request**: When you're ready, submit a PR for review.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions or support, please contact:

- **Email**: [ocdo-bdpd@hc-sc.gc.ca](mailto:ocdo-bdpd@hc-sc.gc.ca)

---

*We are committed to fostering collaboration and innovation within Health Canada and beyond. Explore our repository, contribute, or get in touch to learn more about our work.*
