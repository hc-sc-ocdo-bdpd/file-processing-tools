import os
import numpy as np
import pandas as pd
from typing import List
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from file_processing import Directory
from file_processing import faiss_index
from sentence_transformers import SentenceTransformer

class SearchDirectory:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.has_report = False
        self.is_chunked = False
        self.has_embeddings = False
        self.has_index = False

    def _get_text_chunks(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        chunks = []
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for chunk in splitter.split_text(text):
            chunks.append(chunk)
        return chunks
    
    def _embed_string(self, text: str):
                embedding = self.encoder.encode(text)
                return embedding

    def get_report(self, directory_path: str) -> None:
        directory = Directory(directory_path)
        directory.generate_report(
            report_file = os.path.join(self.folder_path,"report.csv"),
            split_metadata=True,
            include_text=True,
        )
        self.has_report = True

    def chunk_text(self, chunk_size: int = 1024, chunk_overlap: int = 10):
        if self.has_report:
            report_path = os.path.join(self.folder_path,"report.csv")
            df = pd.read_csv(report_path)[['File Path', 'File Name', 'Text']]

            # Initialize an empty list to collect all rows
            all_new_rows = []

            # Get the total number of rows
            total_rows = len(df)
            print(f"Total rows (excluding header): {total_rows}")

            # Process each row with tqdm to show progress
            for index, row in tqdm(df.iterrows(), total=total_rows, desc="Processing rows"):
                file_path = row['File Path']
                content = row['Text']
                file_name = row['File Name']
                
                # Get chunks for the current content
                chunks = self._get_text_chunks(content, chunk_size, chunk_overlap)
                
                # Create new rows for each chunk
                for chunk_text in chunks:
                    new_row = {
                        'file_path': file_path,
                        'file_name': file_name,
                        'content': chunk_text
                    }
                    all_new_rows.append(new_row)

            # Create a new DataFrame from the collected new rows
            chunked_df = pd.DataFrame(all_new_rows)

            # Save the new DataFrame to a new CSV file
            chunked_df.to_csv(os.path.join(self.folder_path, 'data_chunked.csv'), index=False)

            self.is_chunked = True
            print("Chunking complete and saved to 'data_chunked.csv'.")

    def embed_text(self):
        if self.is_chunked:
            df = pd.read_csv(os.path.join(self.folder_path, 'data_chunked.csv'))
            self.encoder = SentenceTransformer("paraphrase-MiniLM-L3-v2")

            tqdm.pandas()
            embeddings = np.array(df['content'].progress_apply(self._embed_string).to_list())

            # Save the new DataFrame to a new CSV file
            np.save(os.path.join(self.folder_path, "embeddings.npy"), embeddings)

            self.has_embeddings = True
            print("Embeddings complete and saved to 'data_embedded.csv'.")

    def create_index(self):
        if self.has_embeddings:
            embeddings = np.load(os.path.join(self.folder_path, "embeddings.npy"))
            index = faiss_index.create_flat_index(embeddings, os.path.join(self.folder_path, "index.faiss"))

            self.has_index = True
            print("FAISS index created and saved to 'index.faiss'.")

    def search(self, query: str, k: int = 1):
        if self.has_index:
            xq = np.expand_dims(self._embed_string(query), axis=0)
            df = pd.read_csv(os.path.join(self.folder_path, 'data_chunked.csv'))
            index = faiss_index.load_index(os.path.join(self.folder_path, "index.faiss"))
            _, indexes = index.query(xq, k)
            return df.iloc[indexes[0]]
