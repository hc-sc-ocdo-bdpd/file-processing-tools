<br>

# Getting started

The file processing library offers 2 imports, `File` and `Directory`, that are used to process files and directories, respectively.

<br>

## File

This import is for extracting metadata from a single file. The code below demonstrates how the `File` object is created:

```py
from file_processing import File

file = File('path/to/file')
```

<br>

### Metadata extraction

Once created, file information can be directly extracted by `file.property_name`. The list of properties are given in the [Introduction](../index.rst). 

For example:

```py
file.access_time
```

It is also possible to show all the file's information. Note that the information will vary between file types. For example, a docx file will have different properties than a pptx file.

```{tab} Code
```python
metadata = file.processor.__dict__
```
```{tab} Output
```python
    {
        'file_path': './requirements.txt,
        'open_file': True,
        'file_name': 'requirements.txt',
        'owner': 'AD/BLUO',
        'extension': '.txt',
        'size': 411,
        'modification_time': 1707156577.8320045,
        'access_time': 1707224508.0667744,
        'creation_time': 1705332838.3662565,
        'parent_directory': 'report',
        'permissions': '666',
        'is_file': True,
        'is_symlink': False,
        'absolute_path': WindowsPath('C:/Users/User/Downloads/report/requirements.txt'),
        'metadata': {
            'text': ...
            'encoding': 'ascii',
            'lines': [...],
            'num_lines': 23,
            'num_words': 22
        }
    }
```

Note: To access properties inside the `metadata` property, use `file.metadata['property_name']`. For example, `file.metadata['text']`.

<br>

### Measuring similarity between 2 files

2 files must be created to use the similarity checker. There are 2 types of similarity checking which are demonstrated below:

```{tab} Cosine Similarity

Cosine similarity rates similarity from -1 to 1 where the higher the score, the more similar the file.

```python
from file_processing import File, CosineSimilarity

a = File('path/to/fileA.docx')
b = File('path/to/fileA.pdf')

CosineSimilarity(a, b).calculate()

>>> 0.6715940803327793
```
```{tab} Levenshtein Distance

Levenshtein distance measures how different 2 files are based on how many characters are different between the 2 files. The smaller the distance, the more similar the files are.

```python
from file_processing import File, LevenshteinDistance

a = File('path/to/fileA.docx')
b = File('path/to/fileA.pdf')

LevenshteinDistance(a, b).calculate()

>>> 4135
```

<br>

## Directory

This import is for extracting information from every file in a directory:

```py
from file_processing import Directory

directory = Directory('path/to/directory')
```

<br>

### Generating a metadata report from a directory

Use `generate_report()` to create a report (.csv) containing information on all files in the directory.

For example, 

```python
directory.generate_report('metadata_report.csv')
```

See more details and examples [here](../2_user_guide/1_directory_report.md)

```{eval-rst}
.. automethod:: file_processing.Directory.generate_report
```

<br>

### Analyzing a directory's metadata

Use `generate_analytics()` to create a report (.csv) that counts the number of files and total size for each file type. This is useful for analyzing the composition of a directory.

```python
directory.generate_analytics('analytics_report.csv')
```

See more details and examples [here](../2_user_guide/2_directory_analytics.md)

```{eval-rst}
.. automethod:: file_processing.Directory.generate_analytics
```

<br>

### Identifying similar files within a directory

Use `identify_duplicates()` to create a report (.csv) that compares file similarities. There are 2 options for this: 
1. Compare every file against each other
2. Return the `top_n` most similar files

See more details and examples [here](../2_user_guide/3_directory_similarity.md)

```{eval-rst}
.. automethod:: file_processing.Directory.identify_duplicates
```

<br>

For an end-to-end example on usage, see the [JupyTer notebook tutorial](https://github.com/hc-sc-ocdo-bdpd/file-processing-tools/blob/main/report_demo.ipynb)