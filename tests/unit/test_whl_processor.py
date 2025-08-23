import os
import shutil
import logging
from unittest.mock import patch
import tempfile
import zipfile
import pytest
from pathlib import Path
from file_processing import File
from file_processing.errors import FileProcessingFailedError
from file_processing_test_data import get_test_files_path

test_files_path = get_test_files_path()

variable_names = "path, package_name, version, python_compatibility, platform_compatibility, non_optional_dependencies, optional_dependencies, author, build_tag"
values = [
    (test_files_path / 'numpy-2.1.2-pp310-pypy310_pp73-win_amd64.whl', "numpy", "2.1.2", ">=3.10", ["Microsoft :: Windows", "POSIX", "Unix", "MacOS"],
     [], [], "Travis E. Oliphant et al.", None),
    (test_files_path / 'pandas-2.2.3-cp313-cp313t-musllinux_1_2_x86_64.whl', "pandas", "2.2.3", ">=3.9", ["OS Independent"],
     ['numpy>=1.22.4; python_version < "3.11"', 'numpy>=1.23.2; python_version == "3.11"',
      'numpy>=1.26.0; python_version >= "3.12"', 'python-dateutil>=2.8.2', 'pytz>=2020.1', 'tzdata>=2022.7'],
     ['hypothesis>=6.46.1 (extra: test)', 'pytest>=7.3.2 (extra: test)', 'pytest-xdist>=2.2.0 (extra: test)',
      'pyarrow>=10.0.1 (extra: pyarrow)', 'bottleneck>=1.3.6 (extra: performance)', 'numba>=0.56.4 (extra: performance)',
      'numexpr>=2.8.4 (extra: performance)', 'scipy>=1.10.0 (extra: computation)', 'xarray>=2022.12.0 (extra: computation)',
      'fsspec>=2022.11.0 (extra: fss)', 's3fs>=2022.11.0 (extra: aws)', 'gcsfs>=2022.11.0 (extra: gcp)',
      'pandas-gbq>=0.19.0 (extra: gcp)', 'odfpy>=1.4.1 (extra: excel)', 'openpyxl>=3.1.0 (extra: excel)',
      'python-calamine>=0.1.7 (extra: excel)', 'pyxlsb>=1.0.10 (extra: excel)', 'xlrd>=2.0.1 (extra: excel)',
      'xlsxwriter>=3.0.5 (extra: excel)', 'pyarrow>=10.0.1 (extra: parquet)', 'pyarrow>=10.0.1 (extra: feather)',
      'tables>=3.8.0 (extra: hdf5)', 'pyreadstat>=1.2.0 (extra: spss)', 'SQLAlchemy>=2.0.0 (extra: postgresql)',
      'psycopg2>=2.9.6 (extra: postgresql)', 'adbc-driver-postgresql>=0.8.0 (extra: postgresql)',
      'SQLAlchemy>=2.0.0 (extra: mysql)', 'pymysql>=1.0.2 (extra: mysql)', 'SQLAlchemy>=2.0.0 (extra: sql-other)',
      'adbc-driver-postgresql>=0.8.0 (extra: sql-other)', 'adbc-driver-sqlite>=0.8.0 (extra: sql-other)',
      'beautifulsoup4>=4.11.2 (extra: html)', 'html5lib>=1.1 (extra: html)', 'lxml>=4.9.2 (extra: html)',
      'lxml>=4.9.2 (extra: xml)', 'matplotlib>=3.6.3 (extra: plot)', 'jinja2>=3.1.2 (extra: output-formatting)',
      'tabulate>=0.9.0 (extra: output-formatting)', 'PyQt5>=5.15.9 (extra: clipboard)', 'qtpy>=2.3.0 (extra: clipboard)',
      'zstandard>=0.19.0 (extra: compression)', 'dataframe-api-compat>=0.1.7 (extra: consortium-standard)',
      'adbc-driver-postgresql>=0.8.0 (extra: all)', 'adbc-driver-sqlite>=0.8.0 (extra: all)',
      'beautifulsoup4>=4.11.2 (extra: all)', 'bottleneck>=1.3.6 (extra: all)',
      'dataframe-api-compat>=0.1.7 (extra: all)', 'fastparquet>=2022.12.0 (extra: all)',
      'fsspec>=2022.11.0 (extra: all)', 'gcsfs>=2022.11.0 (extra: all)', 'html5lib>=1.1 (extra: all)',
      'hypothesis>=6.46.1 (extra: all)', 'jinja2>=3.1.2 (extra: all)', 'lxml>=4.9.2 (extra: all)',
      'matplotlib>=3.6.3 (extra: all)', 'numba>=0.56.4 (extra: all)', 'numexpr>=2.8.4 (extra: all)',
      'odfpy>=1.4.1 (extra: all)', 'openpyxl>=3.1.0 (extra: all)', 'pandas-gbq>=0.19.0 (extra: all)',
      'psycopg2>=2.9.6 (extra: all)', 'pyarrow>=10.0.1 (extra: all)', 'pymysql>=1.0.2 (extra: all)',
      'PyQt5>=5.15.9 (extra: all)', 'pyreadstat>=1.2.0 (extra: all)', 'pytest>=7.3.2 (extra: all)',
      'pytest-xdist>=2.2.0 (extra: all)', 'python-calamine>=0.1.7 (extra: all)', 'pyxlsb>=1.0.10 (extra: all)',
      'qtpy>=2.3.0 (extra: all)', 'scipy>=1.10.0 (extra: all)', 's3fs>=2022.11.0 (extra: all)',
      'SQLAlchemy>=2.0.0 (extra: all)', 'tables>=3.8.0 (extra: all)', 'tabulate>=0.9.0 (extra: all)',
      'xarray>=2022.12.0 (extra: all)', 'xlrd>=2.0.1 (extra: all)', 'xlsxwriter>=3.0.5 (extra: all)',
      'zstandard>=0.19.0 (extra: all)'],
     "The Pandas Development Team", None)
]

@pytest.fixture(params=values, ids=[str(x[0]) for x in values])
def file_obj(request):
    return File(request.param[0])

def test_whl_save(file_obj, caplog):
    caplog.set_level(logging.DEBUG)
    with tempfile.TemporaryDirectory() as temp_dir:
        original_whl_path = file_obj.path
        saved_whl_path = os.path.join(temp_dir, 'SavedPackage.whl')

        file_obj.processor.save(saved_whl_path)

        assert os.path.exists(saved_whl_path)
        assert f"Saving WHL file '{file_obj.path}' to '{saved_whl_path}'." in caplog.text
        assert f"WHL file '{file_obj.path}' saved successfully to '{saved_whl_path}'." in caplog.text

        with zipfile.ZipFile(original_whl_path, 'r') as original_whl, zipfile.ZipFile(saved_whl_path, 'r') as saved_whl:
            assert set(original_whl.namelist()) == set(saved_whl.namelist())  # Check contents are still the same

@pytest.mark.parametrize(variable_names, values)
def test_whl_metadata(path, package_name, version, python_compatibility, platform_compatibility,
                      non_optional_dependencies, optional_dependencies, author, build_tag, caplog):
    caplog.set_level(logging.DEBUG)
    file_obj = File(path)
    file_obj.process()
    metadata = file_obj.metadata

    assert f"Starting processing of WHL file '{file_obj.path}'." in caplog.text
    assert f"Successfully processed WHL file '{file_obj.path}'." in caplog.text

    assert metadata['package_name'] == package_name
    assert metadata['version'] == version
    assert metadata['python_compatibility'] == python_compatibility
    assert metadata['platform_compatibility'] == platform_compatibility
    assert metadata['non_optional_dependencies'] == non_optional_dependencies
    assert metadata['optional_dependencies'] == optional_dependencies
    assert metadata['author'] == author
    assert metadata['build_tag'] == build_tag

@pytest.mark.parametrize(variable_names, values)
def test_save_whl_metadata(copy_file, package_name, version, python_compatibility, platform_compatibility,
                           non_optional_dependencies, optional_dependencies, author, build_tag, caplog):
    test_whl_metadata(copy_file, package_name, version, python_compatibility, platform_compatibility,
                      non_optional_dependencies, optional_dependencies, author, build_tag, caplog)

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_whl_invalid_save_location(path, caplog):
    caplog.set_level(logging.DEBUG)
    whl_file = File(path)
    invalid_save_path = '/non_existent_folder/' + os.path.basename(path)
    with pytest.raises(FileProcessingFailedError):
        whl_file.save(invalid_save_path)
    assert any("Failed to save WHL file" in record.message for record in caplog.records if record.levelname == "ERROR")

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_not_opening_file(path, caplog):
    caplog.set_level(logging.DEBUG)
    with patch('builtins.open', autospec=True) as mock_open:
        file_obj = File(path, open_file=False)
        mock_open.assert_not_called()
        assert f"WHL file '{file_obj.path}' was not opened (open_file=False)." in caplog.text

@pytest.mark.parametrize("file_name", [v[0] for v in values])
@pytest.mark.parametrize("algorithm", ["md5", "sha256"])
def test_whl_copy_with_integrity(file_name, algorithm, tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    path = test_files_path / file_name
    file_obj = File(str(path), open_file=False)
    original_hash = file_obj.processor.compute_hash(algorithm)

    dest_path = tmp_path / Path(file_name).name  # ✅ use just the name
    file_obj.copy(str(dest_path), verify_integrity=True)

    copied = File(str(dest_path))
    assert copied.processor.compute_hash(algorithm) == original_hash

    assert f"Copying file from '{file_obj.file_path}' to '{dest_path}' with integrity verification=True." in caplog.text
    assert f"Integrity verification passed for '{dest_path}'." in caplog.text

@pytest.mark.parametrize("path", map(lambda x: x[0], values))
def test_whl_copy_integrity_failure(path, tmp_path, monkeypatch):
    file_obj = File(path, open_file=False)

    def corrupt_copy(src, dst, *, follow_symlinks=True):
        with open(dst, "w") as f:
            f.write("corrupted content")

    monkeypatch.setattr(shutil, "copy2", corrupt_copy)

    with pytest.raises(FileProcessingFailedError) as excinfo:
        file_obj.copy(tmp_path / os.path.basename(path), verify_integrity=True)
    assert "Integrity check failed" in str(excinfo.value)
