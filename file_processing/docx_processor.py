from file_processor_strategy import FileProcessorStrategy
from docx import Document
from docx.oxml import OxmlElement
from docx2pdf import convert



class DocxFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.metadata = {}

    def process(self) -> None:
        doc = Document(self.file_path)
        self.metadata.update({'text': self.extract_text_from_docx(doc)})
        self.metadata.update({'author': doc.core_properties.author})
        self.metadata.update({'last_modified_by': doc.core_properties.last_modified_by})

        # Other core properties to include: https://python-docx.readthedocs.io/en/latest/api/document.html#coreproperties-objects
        # keywords, language, subject, version


    def save(self, output_path: str = None) -> None:
        doc = Document(self.file_path)

        # Update the core properties (metadata)
        cp = doc.core_properties
        cp.author = self.metadata.get('author', cp.author)
        cp.last_modified_by = self.metadata.get('last_modified_by', cp.last_modified_by)
        
        save_path = output_path or self.file_path
        doc.save(save_path)


    @staticmethod
    def extract_text_from_docx(doc: Document) -> str:
        try:
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except Exception as e:
            print(f"Error encountered while opening or processing {file_path}: {e}")
            return None

    def save_as_txt(self, output_path: str) -> None:
        text = self.extract_text_from_docx(Document(self.file_path))
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)

    def save_as_pdf(self, output_path: str) -> None:
        convert(self.file_path, output_path)