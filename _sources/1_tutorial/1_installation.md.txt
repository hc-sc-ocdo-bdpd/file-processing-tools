<br>

# Installation

<br>

## Quickstart

The library can be installed directly from GitHub. This should take approximately 2-4 minutes.

```js
pip install git+https://github.com/hc-sc-ocdo-bdpd/file-processing-tools.git
```

An alternative option is downloading the `dist/*.whl` file from GitHub and installing this via `pip install <path/to/whl/file>`.

It is not yet possible to directly install the library through `pypi` as the project is in pre-release.

<br>

## Additional Dependencies

This project uses Tesseract for OCR and ffmpeg for transcription. Note that these are not hard requirements as OCR and transcription are configurable by the `use_ocr` and `use_transcription` parameters.

**Tesseract**: This must be installed at: `C:/Users/USERNAME/AppData/Local/Programs/Tesseract-OCR/tesseract.exe` (Windows) or `/usr/bin/tesseract` (Linux). See [here for more details](https://github.com/UB-Mannheim/tesseract/wiki). 

**ffmpeg**: This can be installed through PowerShell:
1. Install scoop: `iwr -useb get.scoop.sh | iex`
2. Install ffmpeg: `scoop install ffmpeg`
3. It may be necessary to restart the IDE and computer after these installs have been completed

<br>

## Optional Dependencies

<br>

### Runtime Optimization with GPU

The audio to text transcription tool can be optimized if your computer supports CUDA, which is a special GPU tool. To toggle this, install the CUDA version of torch:

```
pip install --index-url https://download.pytorch.org/whl/cu118 torch==2.2.0
```

<br>

### Optional Windows Dependencies

To enable file owner information extraction on Windows, you should have the `pywin32` library installed. However, this is not a mandatory dependency as the code will still run normally without `pywin32`.

Use the following command install `pywin32`:

```python
pip install pywin32
```

<br>

## Advanced: Installation for Developers

Optional developer dependencies are defined in the `developer_requirements.txt` file. Once the library is cloned, these can be installed via `pip install -r developer_requirements.txt` or included when creating the venv.

The developer dependencies are listed below and are oriented around build, documentation, and testing capabilities. 

```
wheel==0.40.0
pytest==7.4.0
pytest-order==1.2.0
sphinx==7.2.6
furo==2024.1.29
myst-parser==2.0.0
sphinx-inline-tabs==2023.4.21
ipywidgets==8.1.1
build==1.0.3
```

<br>

### Advanced: Installing using Docker

If you have Docker installed, then you can use it to automatically install all core and developer project dependencies. To do this, follow these 2 steps:

1. Install the `Remote Development` (by Microsoft) extension in VSCode
2. Build the container: View (a tab at the top of the screen) > Command Palette > Dev Containers: Rebuild and Reopen in Container

Note: This does not install GPU and Windows-exclusive dependencies.
