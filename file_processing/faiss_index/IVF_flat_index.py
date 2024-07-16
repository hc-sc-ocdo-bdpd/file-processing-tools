import faiss
import numpy as np
from file_processing.faiss_index import faiss_strategy
from importlib import reload
from file_processing.tools.errors import UnsupportedHyperparameterError
reload(faiss_strategy)

class IVFFlatIndex(faiss_strategy.FAISSStrategy):
    def _create_index(self, embeddings: np.ndarray, nlist: int):
        dimension = embeddings.shape[1]
        if nlist is None:
            nlist = int(np.sqrt(embeddings.shape[0] / 2))
        if not isinstance(nlist, int):
            raise TypeError("nlist must be an int type")
        if nlist < 1:
            raise UnsupportedHyperparameterError("nlist cannot be less than 1")
        if nlist > embeddings.shape[0]:
            raise UnsupportedHyperparameterError(f"nlist value of {nlist} is larger than the number of documents in the index")
        quantizer = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        index.train(embeddings)
        index.add(embeddings)
        return index

    def query(self, xq: np.ndarray, k: int = 1, nprobe: int = 1):
        self.index.nprobe = nprobe
        return self.index.search(xq, k)