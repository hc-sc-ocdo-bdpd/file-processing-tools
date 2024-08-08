import os
import pytest
import shutil
import numpy as np
from file_processing import SearchDirectory

@pytest.fixture(scope="module")
def resource_folder():
    return "tests/resources/similarity_test_files"

@pytest.fixture(scope="module")
def embedding_model():
    return "paraphrase-MiniLM-L3-v2"

# Test chunking step

def test_empty_directory(tmp_path):
    SearchDirectory(tmp_path)
    assert not any(os.scandir(tmp_path))
    
def test_chunk_from_report(resource_folder, tmp_path):
    search = SearchDirectory(tmp_path)
    search.report_from_directory(resource_folder)
    assert os.path.exists(tmp_path / "report.csv")
    search.chunk_text()
    assert os.path.exists(tmp_path / "data_chunked.csv")
    assert os.path.exists(tmp_path / "setup_data.json")

def test_chunk_without_file(tmp_path):
    search = SearchDirectory(tmp_path)
    with pytest.raises(Exception):
        search.chunk_text()

def test_load_chunks_without_csv(tmp_path):
    search = SearchDirectory(tmp_path)
    with pytest.raises(Exception):
        search.chunk_text("tests/resources/directory_test_files/Test_excel_file.xlsx")

def test_load_chunks_with_name_issues(tmp_path):
    search = SearchDirectory(tmp_path)
    with pytest.raises(Exception):
        search.chunk_text("tests/resources/directory_test_files/2021_Census_English.csv")
    
@pytest.fixture()
def directory_with_chunks(resource_folder, tmp_path_factory):
    file_path = tmp_path_factory.mktemp("just_chunks")
    search = SearchDirectory(file_path)
    search.report_from_directory(resource_folder)
    search.chunk_text()
    return file_path

def test_load_with_chunks(directory_with_chunks):
    search = SearchDirectory(directory_with_chunks)
    assert search.n_chunks is not None

def test_load_chunks_different_column_names(directory_with_chunks, tmp_path):
    search1 = SearchDirectory(tmp_path)
    search1.chunk_text("tests/resources/document_search_test_files/report_modified.csv",
                       "path",
                       "content")
    search2 = SearchDirectory(directory_with_chunks)
    assert search2.n_chunks == search1.n_chunks

# Test load embedding step

def test_load_embedding_model(directory_with_chunks, embedding_model):
    search = SearchDirectory(directory_with_chunks)
    search.load_embedding_model(embedding_model)
    assert search.encoder is not None
    assert search.encoding_name == embedding_model

@pytest.fixture(scope="module")
def directory_with_embeding_module(resource_folder, tmp_path_factory, embedding_model):
    file_path = tmp_path_factory.mktemp("with_embedding_module")
    search = SearchDirectory(file_path)
    search.report_from_directory(resource_folder)
    search.chunk_text()
    search.load_embedding_model(embedding_model)
    return file_path

def test_load_after_model_defined(directory_with_embeding_module, embedding_model):
    search = SearchDirectory(directory_with_embeding_module)
    assert search.encoder is not None
    assert search.encoding_name == embedding_model

# Test embedding step

def test_embedding_without_model(directory_with_chunks):
    search = SearchDirectory(directory_with_chunks)
    with pytest.raises(Exception):
        search.embed_text()

variable_names = "start, end, batch, clean_files, expected_files, combined"
values = [
    (0, None, 100, False, ["0-76"], True),
    (0, None, 100, False, ['0-76'], True),
    (10, 40, 10, True, ['0-76'], True),
    (0, None, 20, True, ["0-20", '20-40', '40-60', '60-76'], True),
    (10, None, 30, False, ["10-40", "40-70", "70-76"], False),
    (15, 25, 5, True, ["10-40", "40-70", "70-76"], False),
    (20, 25, 1, True, ["20-21", '21-22', '22-23', '23-24', '24-25'], False),
    (25, 60, 20, False, ['25-45', '45-60'], False),
    (0, None, 15, True, ['0-15', '15-25', '25-45', '45-60', '60-75', '75-76'], True),
    (25, 60, 20, False, ['25-45', '45-60'], False),
    (0, 30, 20, False, ['0-20', '20-25', '25-45', '45-60'], False),
    (50, 100, 15, True, ['0-20', '20-25', '25-45', '45-60', '60-75', '75-76'], True),
    (0, 80, 40, True, ['0-40', '40-76'], True),
    (0, -1, 100, True, ['0-76'], True),
    (-4, -1, 2, True, ['73-75', '75-76'], False),
    (-77, -1, 100, True, ['0-76'], True),
    (-77, 76, 100, True, ['0-76'], True),
    (10, -2, 100, True, ['10-75'], False),
    (-78, None, 100, True, [], False),
    (0, 0, 100, True, [], False),
    (-1, None, 100, True, [], False),
    (76, 80, 100, True, [], False),
    (75, 80, 100, True, ['75-76'], False),
    (0, -77, 100, True, [], False)
]

@pytest.mark.parametrize(variable_names, values)
def test_embedding_creation(directory_with_embeding_module, start, end, batch, clean_files, expected_files, combined):
    search = SearchDirectory(directory_with_embeding_module)
    try:
        if len(expected_files) == 0:
            with pytest.raises(Exception):
                search.embed_text(start, end, batch)
        else:
            search.embed_text(start, end, batch)
        for file in expected_files:
            assert f"embeddings ({file}).npy" in os.listdir(directory_with_embeding_module / "embedding_batches")
        assert os.path.exists(directory_with_embeding_module / "embeddings.npy") == combined
        if combined:
            embeddings = np.load(directory_with_embeding_module / "embeddings.npy")
            assert embeddings.shape[0] == search.n_chunks
    finally:
        # remove created files
        if clean_files:
            shutil.rmtree(directory_with_embeding_module / "embedding_batches")
            if os.path.exists(directory_with_embeding_module / "embeddings.npy"):
                os.remove(directory_with_embeding_module / "embeddings.npy")

def test_overlapping_embedding_files(embedding_model, tmp_path):
    search2 = SearchDirectory(tmp_path)
    search2.chunk_text("tests/resources/document_search_test_files/report_modified.csv",
                       "path",
                       "content")
    search2.load_embedding_model(embedding_model)
    search2.embed_text()
    search1 = SearchDirectory("tests/resources/document_search_test_files")
    search1.chunk_text("tests/resources/document_search_test_files/report_modified.csv",
                       "path",
                       "content")
    search1.load_embedding_model(embedding_model)
    search1.embed_text(batch_size=30)
    try:
        embeddings1 = np.load("tests/resources/document_search_test_files/embeddings.npy")
        embeddings2 = np.load(tmp_path / "embeddings.npy")
        assert np.allclose(embeddings1, embeddings2, atol=1e-5)
    finally:
        os.remove("tests/resources/document_search_test_files/data_chunked.csv")
        os.remove("tests/resources/document_search_test_files/setup_data.json")
        os.remove("tests/resources/document_search_test_files/embeddings.npy")

# Test FAISS search step

def test_flat_faiss_index_creation(directory_with_embeding_module):
    search = SearchDirectory(directory_with_embeding_module)
    try:
        search.embed_text()
        search.create_flat_index()
        assert os.path.exists(directory_with_embeding_module / "index.faiss")
    finally:
        shutil.rmtree(directory_with_embeding_module / "embedding_batches")
        os.remove(directory_with_embeding_module / "embeddings.npy")
        os.remove(directory_with_embeding_module / "index.faiss")

def test_ivf_flat_faiss_index_creation(directory_with_embeding_module):
    search = SearchDirectory(directory_with_embeding_module)
    try:
        search.embed_text()
        search.create_ivf_flat_index()
        assert os.path.exists(directory_with_embeding_module / "index.faiss")
    finally:
        shutil.rmtree(directory_with_embeding_module / "embedding_batches")
        os.remove(directory_with_embeding_module / "embeddings.npy")
        os.remove(directory_with_embeding_module / "index.faiss")

def test_hnsw_faiss_index_creation(directory_with_embeding_module):
    search = SearchDirectory(directory_with_embeding_module)
    try:
        search.embed_text()
        search.create_hnsw_index()
        assert os.path.exists(directory_with_embeding_module / "index.faiss")
    finally:
        shutil.rmtree(directory_with_embeding_module / "embedding_batches")
        os.remove(directory_with_embeding_module / "embeddings.npy")
        os.remove(directory_with_embeding_module / "index.faiss")

@pytest.fixture(scope="module")
def directory_with_faiss(resource_folder, tmp_path_factory, embedding_model):
    file_path = tmp_path_factory.mktemp("with_faiss")
    search = SearchDirectory(file_path)
    search.report_from_directory(resource_folder)
    search.chunk_text()
    search.load_embedding_model(embedding_model)
    search.embed_text()
    search.create_ivf_flat_index()
    return file_path

search_variable_names = "query, k, nprobe"
general_query = "What is the meaning of life, the universe, and everything?"
search_values = [
    (general_query, 3, 1),
    (general_query, 3, 3),
    (general_query, 1, 3)
]

@pytest.mark.parametrize(search_variable_names, search_values)
def test_faiss_search(directory_with_faiss, query, k, nprobe):
    search_ivf = SearchDirectory(directory_with_faiss)
    results_ivf = search_ivf.search(query, k, nprobe)
    assert search_ivf.index.index.nprobe == nprobe
    assert len(results_ivf) == k

def test_search_no_chunks(tmp_path):
    search = SearchDirectory(tmp_path)
    with pytest.raises(Exception):
        search.search("Test")

def test_search_no_embedding_model(directory_with_chunks):
    search = SearchDirectory(directory_with_chunks)
    with pytest.raises(Exception):
        search.search("Test")

def test_search_no_faiss(directory_with_embeding_module):
    search = SearchDirectory(directory_with_embeding_module)
    with pytest.raises (Exception):
        search.search("Test")
