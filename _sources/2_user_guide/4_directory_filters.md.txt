<br>

# Filters

Filters serve as a way to limit the files that appear in the generated CSV reports. It is a parameter for all 3 of the reports (metadata, analytics, similarity).

Filters are best understood through an example - consider the below:

```python
filter = {
    'exclude_str': ['.venv', '.pytest_cache', '.vscode', '__pycache__']
    'include_str': ['file_processing', 'tests', '__init.py__'],
    'extensions': ['.csv', '.docx', '.pptx', '.xlsx', '.pdf'],
    'exclude_extensions': ['.tmp', '', '.py'],
    'min_size': 10000,
    'max_size': 50000
}
```

First, observe that the filter parameter is in the form of a dictionary with specific key names. Not all key names must appear for the filter to be valid. However, the filters are additive - all conditions must be satisfied for the file to appear on the report. Each filter rule performs different operations:

* `exclude_str`: Excludes directories and specific files
* `include_str`: Includes directories and specific files
* `extensions`: Includes file extensions
* `exclude_extensions`: Excludes file extensions
* `min_size`: Minimum file size (in bytes)
* `max_size`: Maximum file size (in bytes)
