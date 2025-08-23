import re
import zipfile
import shutil
import logging
from typing import Union, List
from file_processing.errors import FileProcessingFailedError
from file_processing.file_processor_strategy import FileProcessorStrategy

logger = logging.getLogger(__name__)

class WhlFileProcessor(FileProcessorStrategy):
    """
    Processor for handling Python Wheel (.whl) files, extracting metadata such as package name,
    version, Python compatibility, platform compatibility, optional and non-optional dependencies,
    author, and build tag.

    Attributes:
        metadata (dict): Contains metadata fields including 'package_name', 'version',
                         'python_compatibility', 'platform_compatibility', 'optional_dependencies',
                         'non_optional_dependencies', 'author', and 'build_tag'.
    """

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the WhlFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the .whl file to process.
            open_file (bool): Indicates whether to open and process the file immediately.

        Sets:
            metadata (dict): Populated with a message if `open_file` is False, otherwise initialized with default values.
        """
        super().__init__(file_path, open_file)
        self.metadata = {'message': 'File was not opened'} if not open_file else self._default_metadata()
        if not open_file:
            logger.debug(f"WHL file '{self.file_path}' was not opened (open_file=False).")

    def _default_metadata(self) -> dict:
        """
        Returns default metadata for an unopened .whl file.

        Returns:
            dict: Default metadata fields including 'package_name', 'version',
                  'python_compatibility', 'platform_compatibility', 'optional_dependencies',
                  'non_optional_dependencies', 'author', and 'build_tag'.
        """
        return {
            "package_name": None,
            "version": None,
            "python_compatibility": None,
            "platform_compatibility": None,
            "optional_dependencies": [],
            "non_optional_dependencies": [],
            "author": None,
            "build_tag": None,
        }

    def process(self) -> None:
        """
        Extracts metadata from the .whl file, including package name, version, Python compatibility,
        platform compatibility, optional and non-optional dependencies, author, and build tag.

        Raises:
            FileProcessingFailedError: If the METADATA file is not found or if an error occurs while processing.
        """
        if not self.open_file:
            logger.debug(f"WHL file '{self.file_path}' was not opened (open_file=False).")
            return

        logger.info(f"Starting processing of WHL file '{self.file_path}'.")
        try:
            with zipfile.ZipFile(self.file_path, 'r') as whl_file:
                metadata_file = None
                for name in whl_file.namelist():
                    if name.endswith('.dist-info/METADATA'):
                        metadata_file = name
                        break

                if metadata_file:
                    with whl_file.open(metadata_file) as meta:
                        metadata_content = meta.read().decode('utf-8')
                        logger.debug(f"Read METADATA content from WHL file '{self.file_path}'.")
                        self._extract_metadata(metadata_content)
                else:
                    raise FileProcessingFailedError(f"METADATA file not found in {self.file_path}")
            logger.info(f"Successfully processed WHL file '{self.file_path}'.")
        except Exception as e:
            logger.error(f"Failed to process WHL file '{self.file_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while processing {self.file_path}: {e}"
            )

    def _extract_metadata(self, metadata_content: str) -> None:
        """
        Extracts specific metadata fields from the metadata content.

        Args:
            metadata_content (str): The content of the METADATA file as a string.
        """
        self.metadata["package_name"] = self._extract_metadata_value(metadata_content, "Name")
        self.metadata["version"] = self._extract_metadata_value(metadata_content, "Version")
        self.metadata["python_compatibility"] = self._extract_metadata_value(metadata_content, "Requires-Python")
        self.metadata["author"] = self._extract_author(metadata_content)
        self.metadata["platform_compatibility"] = self._extract_platform_compatibility(metadata_content)
        self.metadata["optional_dependencies"] = self._extract_optional_dependencies(metadata_content)
        self.metadata["non_optional_dependencies"] = self._extract_non_optional_dependencies(metadata_content)
        self.metadata["build_tag"] = self._extract_build_tag()

    def _extract_author(self, content: str) -> str:
        """
        Extracts the author name from the METADATA content.

        Args:
            content (str): The METADATA content as a string.

        Returns:
            str: Author's name, or None if not found.
        """
        match = re.search(r"^Author: (.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        match = re.search(r"^Author-Email: ([^<]+)", content, re.MULTILINE)
        if match:
            return match.group(1).strip().split("<")[0].strip()
        return None

    def _extract_metadata_value(self, content: str, key: str) -> str:
        """
        Extracts a specific metadata value based on the provided key.

        Args:
            content (str): The METADATA content as a string.
            key (str): Metadata key to search for.

        Returns:
            str: Metadata value if found, else None.
        """
        match = re.search(rf"^{key}: (.+)$", content, re.MULTILINE)
        return match.group(1) if match else None

    def _extract_platform_compatibility(self, content: str) -> Union[str, List]:
        """
        Extracts platform compatibility information from the METADATA content.

        Args:
            content (str): The METADATA content as a string.

        Returns:
            Union[str, List]: List of platform compatibility classifiers or an empty list.
        """
        platforms = re.findall(r"^Classifier: Operating System :: (.+)$", content, re.MULTILINE)
        return platforms if platforms else []

    def _extract_optional_dependencies(self, content: str) -> list:
        """
        Extracts optional dependencies from the METADATA content.

        Args:
            content (str): The METADATA content as a string.

        Returns:
            list: List of optional dependencies with extra conditions.
        """
        matches = re.findall(r"^Requires-Dist: (.+); extra == \"(.+)\"", content, re.MULTILINE)
        return [f"{dep} (extra: {extra})" for dep, extra in matches]

    def _extract_non_optional_dependencies(self, content: str) -> list:
        """
        Extracts non-optional dependencies from the METADATA content.

        Args:
            content (str): The METADATA content as a string.

        Returns:
            list: List of non-optional dependencies.
        """
        non_optional_deps = []
        for line in content.splitlines():
            if line.startswith("Requires-Dist:") and "extra ==" not in line:
                dep = line.replace("Requires-Dist:", "").strip()
                non_optional_deps.append(dep)
        return non_optional_deps

    def _extract_build_tag(self) -> str:
        """
        Extracts the build tag from the .whl file name.

        Returns:
            str: Build tag if found, else None.
        """
        file_path_str = str(self.file_path)
        match = re.search(r"-([0-9]+)-", file_path_str)
        return match.group(1) if match else None

    def save(self, output_path: str = None) -> None:
        """
        Saves the .whl file to the specified output path.

        Args:
            output_path (str): Path to save the .whl file. If None, overwrites the original file.

        Raises:
            FileProcessingFailedError: If an error occurs while saving the .whl file.
        """
        save_path = output_path or str(self.file_path)
        logger.info(f"Saving WHL file '{self.file_path}' to '{save_path}'.")
        try:
            shutil.copy2(self.file_path, save_path)
            logger.info(f"WHL file '{self.file_path}' saved successfully to '{save_path}'.")
        except Exception as e:
            logger.error(f"Failed to save WHL file '{self.file_path}' to '{save_path}': {e}")
            raise FileProcessingFailedError(
                f"Error encountered while saving {self.file_path}: {e}"
            )