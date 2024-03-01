<br>

# Analyzing a directory's metadata

```{eval-rst}
.. automethod:: file_processing.Directory.generate_analytics
   :no-index:
```

The `generate_analytics` class method returns a dictionary that stores each file type and its number of files and total file size (in MBs).

The `report_file` is an optional path to the output CSV file. If not specified, then no CSV will be generated the the method will simply return a dictionary containing the analytics.

A filter can be applied to include/exclude file types and directories. See [Filters](./4_directory_filters.md) for more information. 

```{tab} Code
```python
from file_processing import Directory

directory = Directory('./tests/resources/directory_test_files/')
directory.generate_analytics(report_file='./report.csv')
```
```{tab} Output
```python
{
    'size (MB)': {
        '.csv': 5.384414,
        '.docx': 0.019456,
        '.html': 0.168865,
        '.msg': 0.0768,
        '.pdf': 0.443368,
        '.png': 0.004125,
        '.pptx': 100.248831,
        '.rtf': 0.103257,
        '.txt': 0.039357,
        '.xlsx': 0.011885,
        '.xml': 0.004548,
        '.zip': 0.064254
    },
    'count': {
        '.csv': 1,
        '.docx': 1,
        '.html': 1,
        '.msg': 1,
        '.pdf': 2,
        '.png': 1,
        '.pptx': 3,
        '.rtf': 1,
        '.txt': 1,
        '.xlsx': 1,
        '.xml': 1,
        '.zip': 1
    }
}
```
```{tab} CSV
```{image} ../resources/analytics_report.png
:align: center
```
