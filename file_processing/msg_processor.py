from file_processor_strategy import FileProcessorStrategy
import extract_msg
from fpdf import FPDF

class msgFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        self.metadata = {}
    
    def process(self) -> None:
        msg = extract_msg.Message(self.file_path)
        self.metadata.update({'text': msg.body})
        self.metadata.update({'subject': msg.subject})
        self.metadata.update({'date': msg.date})
        self.metadata.update({'sender': msg.sender})
        msg.close()



    def save(self, output_path: str = None) -> None:
        output_path = output_path or self.file_path
        msg_file = extract_msg.Message(self.file_path)
        msg_file.export(path=output_path)
        msg_file.close()
    
    def save_as_txt(self, output_path: str)-> None:
        with open(output_path, 'w', encoding = 'utf-8') as f:
            f.writelines(['Sent by ', (self.metadata['sender']), ' at ', self.metadata['date'], 
                          '\n', 'Subject: ', self.metadata['subject'], '\n', self.metadata['text']])
    
    def save_as_pdf(self, output_path: str) -> None:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size = 12)
        msg_data = []
        msg_data.append([self.metadata['sender'], self.metadata['date'], self.metadata['subject'], self.metadata['text']])

        for x in msg_data:
            x = str(x)
            pdf.multi_cell(200,10, txt = x, align = 'C')
        pdf.output(output_path)