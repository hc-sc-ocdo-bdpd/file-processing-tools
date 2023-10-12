from file_processor_strategy import FileProcessorStrategy
import chardet
from fpdf import FPDF

class TextFileProcessor(FileProcessorStrategy):
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


    def save_as_pdf(self, output_path: str) -> None:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size = 12)
        
        with open(self.file_path, "r") as f:
            for x in f:
                x = x.encode('utf-8').decode('latin1')
                pdf.multi_cell(200,10, txt = x.strip(), align = 'C')
        pdf.output(output_path)
    
    def save_as_docx(self, output_path: str) -> None:
        from docx import Document
        docx_file = Document()
        with open(self.file_path, 'r') as f:
            text = f.read()
            docx_file.add_paragraph(text)

        docx_file.save(output_path)



