:hide-toc: true:

.. toctree::
   :hidden:
   :glob:
   :maxdepth: 2
   :caption: Tutorial:

   1_tutorial/*

.. toctree::
   :hidden:
   :glob:
   :maxdepth: 2
   :caption: User Guide:

   2_user_guide/*

.. toctree::
   :hidden:
   :glob:
   :maxdepth: 2
   :caption: Developer Guide:

   3_developer_guide/*

.. toctree::
   :hidden:
   :glob:
   :maxdepth: 2
   :caption: Additional Information:

   4_additional_information/*

|

===============
File Processing
===============

The file processing library is a metadata extraction tool that supports 26 common file types, 
including OCR for image files and transcription for audio/video files. There are 3 main use cases:

#. | **Extracting metadata from individual files**

#. | **Extracting metadata from files in a directory and generating reports (.csv) that:**

   * | list metadata for each file

   * | provide aggregate statistics on file size and count of each file type

   * | compare file similarity of document-based files to identify possible duplicates in a directory

#. | **Comparing 2 document-based files via cosine similarity and Levenshtein distance**

|

------------------------
Example Usage and Output
------------------------

Test files can be found in `docs/sample_reports` and examples are shown below

.. tab:: Metadata Report

    Lists metadata of all files. There are multiple report configurations and only a subset of the columns are shown:

    .. image:: ./resources/metadata_report.png
       :align: center
     

.. tab:: Analytics Report

    Aggregates file size and count for each file type.

    .. image:: ./resources/analytics_report.png
       :align: center
       :height: 300px
     

.. tab:: Similarity Report (1)

    Compares the text in each document-based file to every other file according to cosine similarity. 

    .. image:: ./resources/cosine_similarity.png
       :align: center
     

.. tab:: Similarity Report (2)

    Determines the top n matches to each file using FAISS indicies.

    .. image:: ./resources/faiss_similarity.png
       :align: center
     

.. tab:: File Metadata

    .. code:: python

        from file_processing import File

        file = File('path/to/file')
        print(file.metadata)

    .. code:: none

        {
            'original_format': 'PNG', 
            'mode': 'RGBA', 
            'width': 1188, 
            'height': 429
        }

|

-------------------------------------------
Supported File Types and Extracted Metadata
-------------------------------------------

|

+--------------------------------+-----------------------+---------------------+
| File Type                      | Metadata Fields       | Example             |
+================================+=======================+=====================+
| [All file types]               | - file_path           | - build/index.html  |
|                                | - file_name           | - index.html        |
|                                | - extension           | - .html             |
|                                | - owner               | - AD/BLUO           |
|                                | - size (in bytes)     | - 53800             |
|                                | - modification_time   | - 1707161382        |
|                                | - access_time         | - 1707161382        |
|                                | - creation_time       | - 1707161382        |
|                                | - permissions         | - 666               |
|                                | - parent_directory    | - build/            |
|                                | - is_file             | - False             |
|                                | - is_symlink          | - False             |
|                                | - absolute_path       | - C:/.../index.html |
+--------------------------------+-----------------------+---------------------+
| `mp3`, `wav`, `mp4`, `flac`,   | - bitrate             | - 50000             |
| `aiff`, `ogg`                  | - length (in seconds) | - 4.32              |
|                                | - artist              | - John Doe          |
|                                | - date                | - 1707161382        |
|                                | - title               | - The ABCs          |
+--------------------------------+-----------------------+---------------------+
| `jpeg`, `png`, `heic`/`heif`,  | - original_format     | - GIF               |
| `tiff`/`tif`                   | - mode                | - P                 |
|                                | - width               | - 1024              |
|                                | - height              | - 980               |
+--------------------------------+-----------------------+---------------------+
| `gif`                          | - original_format     | - GIF               |
|                                | - mode                | - P                 |
|                                | - width               | - 1024              |
|                                | - height              | - 980               |
|                                | - animated            | - True              |
|                                | - frames              | - 24                |
+--------------------------------+-----------------------+---------------------+
| `csv`                          | - text                | - Text goes here    |
|                                | - encoding            | - utf-8             |
|                                | - num_rows            | - 12                |
|                                | - num_cols            | - 5                 |
|                                | - num_cells           | - 60                |
|                                | - empty_cells         | - 5                 |
+--------------------------------+-----------------------+---------------------+
| `xlsx`                         | - active_sheet        | - Sheet1            |
|                                | - sheet_names         | - ["Sheet1"]        |
|                                | - data                | - {"Sheet1": [()]   |
|                                | - last_modified_by    | - John Doe          |
|                                | - creator             | - John Doe          |
|                                | - has_password        | - False             |
+--------------------------------+-----------------------+---------------------+
| `docx`                         | - text                | - Text goes here    |
|                                | - author              | - John Doe          |
|                                | - last_modified_by    | - John Doe          |
|                                | - has_password        | - False             |
+--------------------------------+-----------------------+---------------------+
| `pptx`                         | - text                | - Text goes here    |
|                                | - author              | - John Doe          |
|                                | - last_modified_by    | - John Doe          |
|                                | - num_slides          | - 17                |
|                                | - has_password        | - False             |
+--------------------------------+-----------------------+---------------------+
| `html`, `txt`, `xml`           | - text                | - Text goes here    |
|                                | - encoding            | - utf-8             |
|                                | - lines               | - ["a b c", "d e"]  |
|                                | - words               | - ["Word", "Text"]  |
|                                | - num_lines           | - 2                 |
|                                | - num_words           | - 9                 |
+--------------------------------+-----------------------+---------------------+
| `json`                         | - text                | - Text goes here    |
|                                | - encoding            | - utf-8             |
|                                | - num_keys            | - 3                 |
|                                | - key_names           | - ["A", "B", "C"]   |
|                                | - empty_values        | - 2                 |
+--------------------------------+-----------------------+---------------------+
| `msg`                          | - text                | - Text goes here    |
|                                | - subject             | - "Title"           |
|                                | - date                | - 1707161382        |
|                                | - sender              | - John Doe          |
+--------------------------------+-----------------------+---------------------+
| `pdf`                          | - text                | - Text goes here    |
|                                | - has_password        | - False             |
|                                | - author              | - John Doe          |
|                                | - producer            | - John Doe          |
+--------------------------------+-----------------------+---------------------+
| `py`                           | - num_lines           | - 3                 |
|                                | - num_functions       | - 3                 |
|                                | - num_classes         | - 3                 |
|                                | - imports             | - ["pandas"]        |
|                                | - docstrings          | - ["Docstring A"]   |
+--------------------------------+-----------------------+---------------------+
| `rtf`                          | - text                | - Text goes here    |
+--------------------------------+-----------------------+---------------------+
| `zip`                          | - num_files           | - 1                 |
|                                | - file_types          | - ["html"]          |
|                                | - file_names          | - ["a.html"]        |
+--------------------------------+-----------------------+---------------------+
