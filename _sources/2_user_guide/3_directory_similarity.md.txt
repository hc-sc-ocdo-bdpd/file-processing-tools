<br>

# Identifying similar files within a directory

```{eval-rst}
.. automethod:: file_processing.Directory.identify_duplicates
   :no-index:
```

This method aims to identify similar document-based files in a directory. There are 2 similarity metrics:

* Cosine similarity (`threshold=0`): Compares the cosine similarity (a score between [-1, 1]) of each file against another in a directory
* FAISS indices (`threshold>0`): Indices and retrieves the `top_n` most similar files that satisfy the minimum threshold score. The scores are in the [0,1] range

```{tab} Code
```python
# Sample code to compare all files in a directory
from file_processing import Directory
directory = Directory('./tests/resources/similarity_test_files/')
directory.identify_duplicates(report_file='./docs/sample_reports/similarity_cosine.csv',
                              filters={}, 
                              threshold=0, # Set to 0 to compare all files
                              use_abs_path=True)
```
```{tab} Compare all files
```{image} ../resources/cosine_similarity.png
:align: center
```
```{tab} Find top matches
```{image} ../resources/faiss_similarity.png
:align: center
```