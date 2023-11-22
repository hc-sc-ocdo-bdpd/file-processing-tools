import ast
import shutil
import warnings
from .file_processor_strategy import FileProcessorStrategy
from .errors import FileProcessingFailedError

class PyFileProcessor(FileProcessorStrategy):
    def __init__(self, file_path: str, open_file: bool = True) -> None:
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else self._default_metadata()


    def _default_metadata(self) -> dict:
        return {
            'num_lines': 0,
            'num_functions': 0,
            'num_classes': 0,
            'imports': [],
            'docstrings': []
        }

    def process(self) -> None:
        if not self.open_file:
            return
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.metadata['num_lines'] = len(content.splitlines())
                ast_tree = ast.parse(content)
                self._extract_metadata(ast_tree)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while processing {self.file_path}: {e}")

    def _extract_metadata(self, ast_tree) -> None:
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                self.metadata['num_functions'] += 1
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    self.metadata['docstrings'].append(node.body[0].value.s)
            elif isinstance(node, ast.ClassDef):
                self.metadata['num_classes'] += 1
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    self.metadata['docstrings'].append(node.body[0].value.s)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                self.metadata['imports'].append(ast.unparse(node))

    def save(self, output_path: str = None) -> None:
        if output_path is None:
            output_path = self.file_path
        try:
            shutil.copy2(self.file_path, output_path)
        except Exception as e:
            raise FileProcessingFailedError(f"Error encountered while saving to {output_path}: {e}")
