import zlib
import contextlib
from deca.file import ArchiveFile
from deca.ff_adf import Adf
from pathlib import Path
from apc import config

class FileNotFound(Exception):
    pass

class DecompressedAdfFile():
    def __init__(self, basename: str, filename: Path, file_header: bytearray, header: bytearray, data: bytearray) -> None:
        self.basename = basename
        self.filename = filename
        self.file_header = file_header
        self.header = header
        self.data = data

    def save(self, destination: Path, verbose = False) -> None:
        decompressed_data_bytes = self.header + self.data
        commpressed_data_bytes = self.file_header + _compress_bytes(decompressed_data_bytes)

        adf_file = destination / self.basename
        if verbose:
            print(f"Saving modded file to {adf_file}")
        _save_file(adf_file, commpressed_data_bytes, verbose=verbose)  

class ParsedAdfFile():
    def __init__(self, decompressed: DecompressedAdfFile, adf: Adf) -> None:
        self.decompressed = decompressed
        self.adf = adf

def __get_population_file_name(reserve: str):
    index = config.RESERVES[reserve]["index"]
    return f"animal_population_{index}"

def _get_file_name(reserve: str, mod: bool):
    save_path = config.MOD_DIR_PATH if mod else config.get_save_path()
    filename = save_path / __get_population_file_name(reserve)
    if not filename.exists():
        raise FileNotFound(f'{filename} does not exist')
    return filename

def _read_file(filename: Path, verbose = False):
    if verbose:
        print(f"Reading {filename}")
    return filename.read_bytes()

def _decompress_bytes(data_bytes: bytearray) -> bytearray:
    decompress = zlib.decompressobj()
    decompressed = decompress.decompress(data_bytes)
    decompressed = decompressed + decompress.flush()
    return decompressed

def _compress_bytes(data_bytes: bytearray) -> bytearray:
    compress = zlib.compressobj()
    compressed = compress.compress(data_bytes)
    compressed = compressed + compress.flush()
    return compressed

def _save_file(filename: Path, data_bytes: bytearray, verbose = False):
    Path(filename.parent).mkdir(exist_ok=True)
    filename.write_bytes(data_bytes)
    if verbose:
        print(f"Saved {filename}")

def _parse_adf_file(filename: Path, suffix: str = None, verbose = False) -> Adf:
    obj = Adf()
    with ArchiveFile(open(filename, 'rb')) as f:
        with contextlib.redirect_stdout(None):
            obj.deserialize(f)
    content = obj.dump_to_string()
    suffix = f"_{suffix}.txt" if suffix else ".txt"
    txt_filename = config.APP_DIR_PATH / f".working/{filename.name}{suffix}"
    _save_file(txt_filename, bytearray(content, 'utf-8'), verbose)            
    return obj

def _decompress_adf_file(filename: Path, verbose = False) -> DecompressedAdfFile:
    # read entire adf file
    data_bytes = _read_file(filename, verbose)
    data_bytes = bytearray(data_bytes)

    # split out header
    header = data_bytes[0:32]
    data_bytes = data_bytes[32:]

    # decompress data
    decompressed_data_bytes = _decompress_bytes(data_bytes)
    decompressed_data_bytes = bytearray(decompressed_data_bytes)

    # split out compression header
    decompressed_header = decompressed_data_bytes[0:5]
    decompressed_data_bytes = decompressed_data_bytes[5:]

    # save uncompressed adf data to file
    parsed_basename = filename.name
    adf_file = config.APP_DIR_PATH / f".working/{parsed_basename}_sliced"
    _save_file(adf_file, decompressed_data_bytes, verbose)

    return DecompressedAdfFile(
        parsed_basename,
        adf_file,
        header,
        decompressed_header,
        decompressed_data_bytes
    )

def parse_adf(filename: Path, suffix: str = None, verbose = False) -> Adf:
    if verbose:
        print(f"Parsing {filename}")
    return _parse_adf_file(filename, suffix, verbose=verbose)

def load_adf(filename: Path, verbose = False) -> ParsedAdfFile:
    data = _decompress_adf_file(filename, verbose=verbose)
    adf = parse_adf(data.filename, verbose=verbose)
    return ParsedAdfFile(data, adf)

def load_reserve(reserve_name: str, mod: bool = False, verbose = False) -> ParsedAdfFile:
    filename = _get_file_name(reserve_name, mod)
    return load_adf(filename, verbose=verbose)
