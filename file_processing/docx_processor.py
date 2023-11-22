from zipfile import BadZipFile
from docx.oxml import OxmlElement
import msoffcrypto
from io import BytesIO
from .file_processor_strategy import FileProcessorStrategy
from .docx import Document
from .errors import FileProcessingFailedError, FileCorruptionError

class DocxFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else self._default_metadata()



    def _default_metadata(self) -> dict:
        return {
            'text': None,
            'author': None,
            'last_modified_by': None,
            'has_password': False
        }


    def process(self) -> None:
        if not self.open_file:
            return

        with open(self.file_path, 'rb') as f:
            file_content = BytesIO(f.read())

        try:
            office_file = msoffcrypto.OfficeFile(file_content)
            if office_file.is_encrypted():
                self.metadata["has_password"] = True
                return
        except Exception as e:
            raise FileCorruptionError(f"File is corrupted: {self.file_path}")


        try:
            file_content.seek(0)  # Reset the position to the start
            doc = Document(file_content)
            self.metadata.update({'text': self.extract_text_from_docx(doc)})
            self.metadata.update({'author': doc.core_properties.author})
            self.metadata.update({'last_modified_by': doc.core_properties.last_modified_by})
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing {self.file_path}: {e}")



    def save(self, output_path: str = None) -> None:
        try:
            doc = Document(self.file_path)

            # Update the core properties (metadata)
            cp = doc.core_properties
            cp.author = self.metadata.get('author', cp.author)
            cp.last_modified_by = self.metadata.get('last_modified_by', cp.last_modified_by)
            
            save_path = output_path or self.file_path
            doc.save(save_path)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving to {save_path}: {e}")


    @staticmethod
    def extract_text_from_docx(doc: Document) -> str:
        try:
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Error encountered while opening or processing {self.file_path}: {e}")
            return None