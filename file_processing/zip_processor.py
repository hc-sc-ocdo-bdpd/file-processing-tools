import zipfile
from pathlib import Path
import shutil
from .file_processor_strategy import FileProcessorStrategy
from .errors import FileProcessingFailedError

class ZipFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else {}
    
    def process(self) -> None:
        if not self.open_file:
            return

        try:
            z = zipfile.ZipFile(self.file_path, 'r')
            self.metadata.update({"num_files": len(z.infolist())})
            self.metadata.update({"file_types": self.extract_file_types(z)})
            self.metadata.update({"file_names": z.namelist()})
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing {self.file_path}: {e}")


    @staticmethod
    def extract_file_types(z):
        try:
            types = dict()
            for info in z.infolist():
                fname = info.filename
                ext = fname[fname.find('.') + 1:]
                if ext in types.keys():
                    types[ext] = types[ext] + 1
                else:
                    types[ext] = 1
            return types
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while extracting file types: {e}")


    
    def extract(self, output_dir: str = None) -> None:
        try:
            if not output_dir:
                output_dir = self.file_path.with_suffix('')

            Path(output_dir).mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while extracting {self.file_path}: {e}")



    def save(self, output_path: str = None) -> None:
        try:
            output_path = output_path or str(self.file_path)
            shutil.copy2(self.file_path, output_path)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving {self.file_path}: {e}")