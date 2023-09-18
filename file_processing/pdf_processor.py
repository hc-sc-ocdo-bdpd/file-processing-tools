from file_processor_strategy import FileProcessorStrategy
from PyPDF2 import PdfReader
import os
import pandas as pd
from pdf2docx import Converter

class PdfFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.metadata = {}

    def process(self) -> None:
        text = self.extract_text_from_pdf(self.file_path)
        self.metadata.update({'text': text})

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

    def extract_tbls_from_pdf(file_path: str) -> str:
        doc_path = file_path.rsplit('.', 1)[0].lower() + ".docx"
        head, tail = os.path.split(file_path)
        doc = head.rsplit('.', 1)[0].lower()
        writer = pd.ExcelWriter(file_path.rsplit('.', 1)[0].lower()+'_tbls.xlsx', engine='xlsxwriter', engine_kwargs={'options': {'encoding': 'utf8'}})
        try:
            cv = Converter(file_path)
            tables = cv.extract_tables(start=0, end=None)
            cv.close()
            for count, table in enumerate(tables):
                df = pd.DataFrame(table)
                df = df.apply(lambda x: [r.encode("utf8").split(b";base64,")[0].replace(b'\xef\xbf\xbd',b' ').decode("utf8") for r in x])
                df.to_excel(writer, sheet_name=doc[:20]+"_tbl_"+str(count))
            writer.close()
        except Exception as e:
            print(f"Error encountered while opening or processing {file_path}: {e}")