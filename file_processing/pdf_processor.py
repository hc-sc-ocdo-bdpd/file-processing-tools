from file_processor_strategy import FileProcessorStrategy
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter

class PdfFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.metadata = {}

    def process(self) -> None:
        text = self.extract_text_from_pdf(self.file_path)
        self.metadata.update({'text': text})
    
    def save(self, output_path: str = None) -> None:
        output_path = output_path or self.file_path

        pdf_read = PdfReader(self.file_path)
        pdf = PdfWriter(self.file_path)

        for page in range(len(pdf_read.pages)):
            # Add each page to the writer object
            pdf.add_page(pdf_read.pages[page])

        with open(output_path, 'wb') as output_pdf:
            pdf.write(output_pdf)

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error encountered while opening or processing {file_path}: {e}")
            return None
    
    def save_as_txt(self, output_path: str) -> None:
        import chardet
        text = self.extract_text_from_pdf(self.file_path)
        encoding = chardet.detect(open(self.file_path, "rb").read())['encoding']
        with open(output_path, 'w', encoding = encoding) as f:
            f.write(text)
    
    def save_as_docx(self, output_path: str):
        from docx import Document
        text = self.extract_text_from_pdf(self.file_path)
        docx_file = Document()
        docx_file.add_paragraph(text)
        docx_file.save(output_path)
    