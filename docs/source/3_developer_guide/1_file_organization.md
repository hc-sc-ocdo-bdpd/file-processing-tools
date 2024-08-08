<br>

# File Organization

This project follows the standard Python project setup with the `src` folder (`file_processing/`) and `tests` folder for unit tests. 

| Path | File | Purpose |
| ---- | ---- | ------- |
| `.github/workflows` | `CI.yaml` | Runs unit tests upon PR to main |
| | `sphinx.yml` | Builds and extracts documentation to `gh-pages` branch upon push to main which triggers a process to publish the documentation |
| `dist` | | Contains the build files from `python -m build` that users can `pip install`. These files are uploaded to `pypi` |
| `docs` | | Contains project documentation and sample output. Can be built locally via `docs/make html` |
| `file_processing/faiss_index` | | Collection of functions that create and load different types of supported FAISS indexes |
| `file_processing/processors` | | File-specific metadata extractors for each supported file type |
| `file_processing/similarity` | | Standalone utils for calculating `CosineSimilarity` and `LevenshteinDistance` between 2 files | 
| `file_processing/tools` | | Helper methods (OCR, transcription, custom errors, templates) |
| `file_processing` | `directory.py` | The `Directory()` class used to process directories by iteratively converting each file into a `File()` object to extract metadata |
| `file_processing` | `file.py` | The `File()` class used to process individual files. Maps the given file path to the respective processor in `file_processing/processor` then extracts the metadata |
| `file_processing` | `search_directory.py` | The `SearchDirectory()` class used to chunk text, create embeddings, and FAISS indexes to create a semantically searchable database from a directory |
| `tests` | | Contains test code. Can be run via `pytest tests/` |
| `tests` | `resources` | Contains all test files which include files of various file types |
| `.` | `pyproject.toml` | Defines the build requirements for the project. Used to generate the `dist/` files via `python -m build` |
| `.` | `requirements.txt` | Lists project dependencies. Can be installed via `pip install -r requirements.txt` |
