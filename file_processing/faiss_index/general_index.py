import faiss
import numpy as np
from file_processing.faiss_index import faiss_strategy
from importlib import reload
reload(faiss_strategy)

class GeneralIndex(faiss_strategy.FAISSStrategy):
    def _create_index(self):
        raise(NotImplementedError)

    def query(self, xq: np.ndarray, k: int = 1):
        return self.index.search(xq, k)