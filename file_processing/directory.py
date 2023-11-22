import os
import csv
from typing import Optional
import json
from tqdm import tqdm
from .file import File

class Directory:
    def __init__(self, path: str, use_ocr: bool = False) -> None:
        self.path = path
        self.use_ocr = use_ocr


    def _file_generator(self, filters: dict = None, open_files: bool = True):
        filters = filters or {}
        for root, _, filenames in os.walk(self.path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file = File(file_path, use_ocr=self.use_ocr, open_file=open_files)
                if not self._apply_filters(file, filters):
                    continue
                yield file


    def _apply_filters(self, file: File, filters: dict) -> bool:
        if filters.get('extensions') and file.extension not in filters['extensions']:
            return False
        
        if filters.get('min_size') and file.size < filters['min_size']:
            return False
        if filters.get('max_size') and file.size > filters['max_size']:
            return False
        
        # Additional filter conditions can be added here as needed
        
        return True  # Passes all filter conditions


    def get_files(self, filters: dict = None):
        return self._file_generator(filters)


    def generate_report(self, report_file: str, include_text: bool = True, filters: Optional[dict] = None, keywords: Optional[list] = None, open_files: bool = True) -> None:
        """
        Generates a report of the directory and writes it to a CSV file.

        :param report_file: The path to the output CSV file.
        :param include_text: Whether to include the 'text' attribute in the metadata column.
        :param filters: A dictionary of filters to apply to the files.
        :param keywords: A list of keywords to count in the 'text' attribute of the metadata.
        :param open_files: Whether to open the files for extracting metadata. If False, files won't be opened.
        """

        try:
            # Count the total number of files that match the filters
            total_files = sum(1 for _ in self._file_generator(filters, open_files=open_files))
            
            with open(report_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Modify the header row to include the 'Keywords' column if keywords are provided
                header_row = ['File Path', 'File Name', 'Extension', 'Size', 'Modification Time', 'Access Time', 'Metadata']
                if keywords:
                    header_row.append('Keywords')
                
                writer.writerow(header_row)
                
                # Iterate over each file in the directory and write the information to the CSV file
                with tqdm(total=total_files, desc='Generating Report', unit='file') as pbar:
                    for file in self._file_generator(filters, open_files=open_files):
                        metadata = file.metadata.copy()
                        if not include_text or not open_files:
                            metadata.pop('text', None)  # Remove the 'text' attribute if it exists and include_text is False or files are not opened
                        
                        row_data = [
                            file.file_path,
                            file.file_name,
                            file.extension,
                            file.size,
                            file.modification_time,
                            file.access_time,
                            json.dumps(metadata, ensure_ascii=False)  # Convert metadata to a JSON string
                        ]
                        
                        if keywords and include_text and open_files:
                            text = metadata.get('text', '')
                            if text is None: # if {text: null} in metadata
                                text = ''
                            keyword_counts = self._count_keywords(text, keywords)
                            row_data.append(json.dumps(keyword_counts, ensure_ascii=False))
                        
                        writer.writerow(row_data)
                        pbar.update(1)
        except Exception as e:
            raise


    def _count_keywords(self, text: str, keywords: list) -> dict:
        """
        Counts the occurrences of each keyword in the given text.

        :param text: The text to search in.
        :param keywords: The list of keywords to count.
        :return: A dictionary with the keywords as keys and their counts as values.
        """

        keyword_dict = {}
        text = text.lower()

        for keyword in keywords:
            count = text.count(keyword.lower())
            keyword_dict[keyword] = count

        return keyword_dict



