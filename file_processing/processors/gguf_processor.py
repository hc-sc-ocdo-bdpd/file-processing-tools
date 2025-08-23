import struct
import logging
from file_processing.file_processor_strategy import FileProcessorStrategy
from file_processing.errors import FileProcessingFailedError

logger = logging.getLogger(__name__)

class GgufFileProcessor(FileProcessorStrategy):
    """
    Processor for handling GGUF files, extracting metadata and tensor information.

    Attributes:
        GGUF_MAGIC_NUMBER (bytes): Magic number used to identify GGUF files.
        VALUE_FORMATS (dict): Mapping of value types to struct formats for unpacking.
        TENSOR_TYPES (dict): Mapping of tensor type identifiers to tensor type names.
        metadata (dict): Extracted metadata, including key-value pairs and tensor information.
        tensors_info (list): Information about tensors in the file.
    """

    GGUF_MAGIC_NUMBER = b"GGUF"
    VALUE_FORMATS = {
        0: "B",  # UINT8
        1: "b",  # INT8
        2: "H",  # UINT16
        3: "h",  # INT16
        4: "I",  # UINT32
        5: "i",  # INT32
        6: "f",  # FLOAT32
        7: "?",  # BOOL
        10: "Q",  # UINT64
        11: "q",  # INT64
        12: "d",  # FLOAT64
    }
    TENSOR_TYPES = {
        0: "GGML_TYPE_F32",
        1: "GGML_TYPE_F16",
        2: "GGML_TYPE_Q4_0",
        3: "GGML_TYPE_Q4_1",
        6: "GGML_TYPE_Q5_0",
        7: "GGML_TYPE_Q5_1",
        8: "GGML_TYPE_Q8_0",
        9: "GGML_TYPE_Q8_1",
        10: "GGML_TYPE_Q2_K",
        11: "GGML_TYPE_Q3_K",
        12: "GGML_TYPE_Q4_K",
        13: "GGML_TYPE_Q5_K",
        14: "GGML_TYPE_Q6_K",
        15: "GGML_TYPE_Q8_K",
        16: "GGML_TYPE_IQ2_XXS",
        17: "GGML_TYPE_IQ2_XS",
        18: "GGML_TYPE_IQ3_XXS",
        19: "GGML_TYPE_IQ1_S",
        20: "GGML_TYPE_IQ4_NL",
        21: "GGML_TYPE_IQ3_S",
        22: "GGML_TYPE_IQ2_S",
        23: "GGML_TYPE_IQ4_XS",
        24: "GGML_TYPE_I8",
        25: "GGML_TYPE_I16",
        26: "GGML_TYPE_I32",
        27: "GGML_TYPE_I64",
        28: "GGML_TYPE_F64",
        29: "GGML_TYPE_IQ1_M",
    }

    def __init__(self, file_path: str, open_file: bool = True) -> None:
        """
        Initializes the GgufFileProcessor with the specified file path.

        Args:
            file_path (str): Path to the GGUF file to process.
            open_file (bool): Indicates whether to open and process the file.
        """
        super().__init__(file_path, open_file)
        self.magic_number = None
        self.version = None
        self.metadata = None
        self.tensors_info = None
        self.alignment = None

    def process(self) -> None:
        """
        Processes the GGUF file, extracting metadata, tensor count, and tensor information.

        Raises:
            FileProcessingFailedError: If an error occurs or the file does not match expected format.
        """
        logger.info(f"Starting processing of GGUF file '{self.file_path}'.")

        if not self.open_file:
            logger.debug(f"GGUF file '{self.file_path}' was not opened (open_file=False).")
            return
        try:
            with open(self.file_path, "rb") as f:
                self.magic_number = f.read(4)
                if self.magic_number != self.GGUF_MAGIC_NUMBER:
                    raise FileProcessingFailedError("Invalid GGUF magic number.")

                logger.debug(f"Detected magic number '{self.magic_number.decode('utf-8')}' for GGUF file '{self.file_path}'.")

                self.version = struct.unpack("I", f.read(4))[0]
                if self.version != 3:
                    raise FileProcessingFailedError("Unsupported GGUF version.")

                logger.debug(f"GGUF version: {self.version}")

                tensor_count = struct.unpack("Q", f.read(8))[0]
                metadata_kv_count = struct.unpack("Q", f.read(8))[0]

                self.metadata = {}
                for _ in range(metadata_kv_count):
                    key, value = self._read_metadata_kv(f)
                    self.metadata[key] = value
                logger.debug(f"Extracted {metadata_kv_count} metadata entries from GGUF file '{self.file_path}'.")

                self.alignment = self.metadata.get("general.alignment", 1)

                self.tensors_info = []
                for _ in range(tensor_count):
                    tensor_info = self._read_tensor_info(f)
                    self.tensors_info.append(tensor_info)

                logger.debug(f"Extracted {tensor_count} tensors from GGUF file '{self.file_path}'.")

                self.metadata.update({
                    "magic_number": self.magic_number.decode("utf-8"),
                    "version": self.version,
                    "tensor_count": tensor_count,
                    "alignment": self.alignment,
                    "tensors_info": self.tensors_info
                })

                logger.info(f"Successfully processed GGUF file '{self.file_path}'.")

        except Exception as e:
            logger.error(f"Failed to process GGUF file '{self.file_path}': {e}")
            raise FileProcessingFailedError(f"Error processing GGUF file {self.file_path}: {e}")

    def _read_string(self, f) -> str:
        """
        Reads a string from the GGUF file.

        Args:
            f (file object): Opened GGUF file.

        Returns:
            str: Decoded string from the file.
        """
        length = struct.unpack("Q", f.read(8))[0]
        return f.read(length).decode("utf-8")

    def _read_metadata_kv(self, f):
        """
        Reads a metadata key-value pair from the GGUF file.

        Args:
            f (file object): Opened GGUF file.

        Returns:
            tuple: Key-value pair, where key is a string and value varies by type.
        """
        key = self._read_string(f)
        value_type = struct.unpack("I", f.read(4))[0]
        value = self._read_value(f, value_type)
        return key, value

    def _read_value(self, f, value_type):
        """
        Reads a value from the GGUF file based on its type.

        Args:
            f (file object): Opened GGUF file.
            value_type (int): Type identifier for the value.

        Returns:
            Any: Value read from the file, format depends on type.

        Raises:
            FileProcessingFailedError: If an unsupported value type is encountered.
        """
        if value_type in self.VALUE_FORMATS:
            return struct.unpack(
                self.VALUE_FORMATS[value_type],
                f.read(struct.calcsize(self.VALUE_FORMATS[value_type]))
            )[0]
        if value_type == 8:  # STRING
            return self._read_string(f)
        if value_type == 9:  # ARRAY
            array_type = struct.unpack("I", f.read(4))[0]
            array_len = struct.unpack("Q", f.read(8))[0]
            return [self._read_value(f, array_type) for _ in range(array_len)]
        raise FileProcessingFailedError(f"Unsupported GGUF value type: {value_type}")

    def _read_tensor_info(self, f) -> dict:
        """
        Reads tensor information from the GGUF file.

        Args:
            f (file object): Opened GGUF file.

        Returns:
            dict: Dictionary containing tensor details.
        """
        name = self._read_string(f)
        n_dimensions = struct.unpack("I", f.read(4))[0]
        dimensions = struct.unpack(f"{n_dimensions}Q", f.read(8 * n_dimensions))
        tensor_type = struct.unpack("I", f.read(4))[0]
        offset = struct.unpack("Q", f.read(8))[0]
        return {
            "name": name,
            "n_dimensions": n_dimensions,
            "dimensions": dimensions,
            "type": self.TENSOR_TYPES.get(tensor_type, "UNKNOWN"),
            "offset": offset
        }

    def save(self, output_path: str = None) -> None:
        """No save implementation needed for GGUF files (read-only)."""
        logger.info(f"Save skipped for read-only GGUF file '{self.file_path}'.")
        pass
