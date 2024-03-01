<br>

# Limitations and Future Work

<br>

## Modifying Metadata

The library can only read metadata and save the file in another location. However, it may be desirable to modify a file's metadata. For example, assigning an 'Author' or adding custom metadata fields for organization purposes. The challenge with this is that certain metadata fields are immutable depending on the file system and file type. For example, it is generally impossible to edit `Access Time` and file `Owner` fields on Windows. 

<br>

## Rollback Functionality

Tying into the modification of metadata is the use case of rolling back changes. For example, the program can be used to generate a report that tracks all metadata values at a point in time. If the files were incorrectly modified, say the file permissions were changed to 666, then the idea is to revert every file back to a previous version. In this way, metadata reports can serve as backups.

<br>

## File Conversion

Another feature that ties into file processing is the ability to convert between similar file types. That is, conversion within image, audio, and document-based files. The challenge here is first creating a generic converter that can accept any file type and convert it to a new type, and then writing unit tests to assert the new file is valid.

<br>

## GitHub Issues

There are various enhancements suggested in the [GitHub Issues](https://github.com/hc-sc-ocdo-bdpd/file-processing-tools/issues) menu. These vary from cloud support to expanding supported file types and implementing means of reducing runtime. 
