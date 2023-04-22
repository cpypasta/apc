import zlib, contextlib, random, math
from deca.file import ArchiveFile
from deca.ff_adf import Adf
from pathlib import Path
from apc import config
from apc.adf_profile import *

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

def _get_file_name(reserve: str, mod: bool) -> Path:
    save_path = config.MOD_DIR_PATH if mod else config.get_save_path()
    if save_path is None:
        raise FileNotFound("Please configure your game save path")
    filename = save_path / config.get_population_file_name(reserve)
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

def _update_non_instance_offsets(data: bytearray, profile: dict, added_size: int) -> None:
  offsets_to_update = [
    (profile["header_instance_offset"], profile["instance_header_start"]),
    (profile["header_typedef_offset"], profile["typedef_start"]),
    (profile["header_nametable_offset"], profile["nametable_start"]),
    (profile["header_total_size_offset"], profile["total_size"]),
    (profile["instance_header_start"]+12, profile["details"]["instance_offsets"]["instances"][0]["size"])
  ]
  for offset in offsets_to_update:
    write_value(data, create_u32(offset[1] + added_size), offset[0])

def _insert_animal(data: bytearray, animal: Animal, array: AdfArray) -> None:
  write_value(data, create_u32(read_u32(data[array.header_length_offset:array.header_length_offset+4])+1), array.header_length_offset)
  animal_bytes = animal.to_bytes()
  data[array.array_org_end_offset:array.array_org_end_offset] = animal_bytes

def _remove_animal(data: bytearray, array: AdfArray) -> None:
  write_value(data, create_u32(read_u32(data[array.header_length_offset:array.header_length_offset+4])-1), array.header_length_offset)
  del data[array.array_org_end_offset-32:array.array_org_end_offset]

def _update_instance_arrays(data: bytearray, animal_arrays: List[AdfArray], target_array: AdfArray, size: int):
  for animal_array in animal_arrays:
    if animal_array.array_start_offset >= target_array.array_end_offset and animal_array.array_start_offset != 0:
      animal_array.array_start_offset = animal_array.array_start_offset + size
      animal_array.array_end_offset = animal_array.array_end_offset + size
      animal_array.rel_array_start_offset = animal_array.rel_array_start_offset + size
      write_value(data, create_u32(animal_array.rel_array_start_offset), animal_array.header_array_offset)


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

# TODO: EXPERIMENT
def add_animals_to_reserve(reserve_name: str, species_key: str, animals: List[Animal], verbose: bool, mod: bool) -> None:
  if len(animals) == 0:
    return
  org_filename = _get_file_name(reserve_name, mod)
  decompressed_adf = _decompress_adf_file(org_filename, verbose=verbose)
  profile = create_profile(decompressed_adf.filename)
  population_index = config.RESERVES[reserve_name]["species"].index(species_key)
  animal_arrays, other_arrays = find_arrays(profile)
  all_arrays = animal_arrays+other_arrays
  eligible_animal_arrays = [x for x in animal_arrays if x.population == population_index]
  eligible_animal_arrays = sorted(eligible_animal_arrays, key=lambda x: x.array_start_offset, reverse=True)
  reserve_data = decompressed_adf.data
  
  # _update_non_instance_offsets(reserve_data, profile, 32)
  # reserve_data[193712+8:193712+12] = create_u32(read_u32(reserve_data[193712+8:193712+12])+1) # increase array length
  # print("updating", read_u32(reserve_data[120:124]), "to", 217192+4-96)
  # reserve_data[120:120+4] = create_u32(217192+32-96) # increase array offset, hunting pressure
  # animal = Animal("male", 1.0, 1.0, False, 1234)
  # reserve_data[217192:217192] = animal.to_bytes() # add element to array
  
  # reserve_data[-1:-1] = bytearray(struct.pack("B", 23))
  
  reserve_data[284338:284339] = bytearray(struct.pack("c", "y".encode()))
  
  decompressed_adf.save(config.MOD_DIR_PATH, verbose=verbose)

def add_animals_to_reserve2(reserve_name: str, species_key: str, animals: List[Animal], verbose: bool, mod: bool) -> None:
  if len(animals) == 0:
    return
  org_filename = _get_file_name(reserve_name, mod)
  decompressed_adf = _decompress_adf_file(org_filename, verbose=verbose)
  profile = create_profile(decompressed_adf.filename)
  population_index = config.RESERVES[reserve_name]["species"].index(species_key)
  animal_arrays, other_arrays = find_arrays(profile)
  all_arrays = animal_arrays+other_arrays
  eligible_animal_arrays = [x for x in animal_arrays if x.population == population_index]
  eligible_animal_arrays = sorted(eligible_animal_arrays, key=lambda x: x.array_start_offset, reverse=True)
  reserve_data = decompressed_adf.data
  
  total_size = animals[0].size * len(animals)
  _update_non_instance_offsets(reserve_data, profile, total_size)
  n = 1 if len(animals) < len(eligible_animal_arrays) else math.ceil(len(animals) / len(eligible_animal_arrays))
  animal_chunks = [animals[i:i + n] for i in range(0, len(animals), n)]
  for i, animal_chunk in enumerate(animal_chunks):
    chosen_array = eligible_animal_arrays[i]
    for animal in animal_chunk:
      _update_instance_arrays(reserve_data, all_arrays, chosen_array, animal.size)
  for i, animal_chunk in enumerate(animal_chunks):
    chosen_array = eligible_animal_arrays[i]    
    for animal in animal_chunk:
      _insert_animal(reserve_data, animal, chosen_array)
  decompressed_adf.save(config.MOD_DIR_PATH, verbose=verbose)

def remove_animals_from_reserve(reserve_name: str, species_key: str, animal_cnt: int, verbose: bool, mod: bool) -> None:
  if animal_cnt == 0:
    return
  org_filename = _get_file_name(reserve_name, mod)
  decompressed_adf = _decompress_adf_file(org_filename, verbose=verbose)
  profile = create_profile(decompressed_adf.filename)
  population_index = config.RESERVES[reserve_name]["species"].index(species_key)
  animal_arrays, other_arrays = find_arrays(profile)
  all_arrays = animal_arrays+other_arrays
  eligible_animal_arrays = [x for x in animal_arrays if x.population == population_index]
  eligible_animal_arrays = sorted(eligible_animal_arrays, key=lambda x: x.array_start_offset, reverse=True)
  reserve_data = decompressed_adf.data 
  animal_size = 32
  
  animals_left_to_remove = animal_cnt
  arrays_to_remove_from = []
  for animal_array in eligible_animal_arrays:
    if animals_left_to_remove == 0:
      break
    array_length = animal_array.length
    if array_length > 1:
      remove_cnt = array_length - 1 if (array_length - 1) < animals_left_to_remove else animals_left_to_remove
      arrays_to_remove_from.append((remove_cnt, animal_array))
      animals_left_to_remove = animals_left_to_remove - remove_cnt
  if animals_left_to_remove > 0:
    raise Exception("Not enough animals to remove")
      
  total_size = animal_size * animal_cnt
  _update_non_instance_offsets(reserve_data, profile, -total_size)
  for remove_cnt, animal_array in arrays_to_remove_from:
    _update_instance_arrays(reserve_data, all_arrays, animal_array, -(animal_size*remove_cnt))
  for remove_cnt, animal_array in arrays_to_remove_from:
    for i in range(remove_cnt):
      _remove_animal(reserve_data, animal_array)\
  
  decompressed_adf.save(config.MOD_DIR_PATH, verbose=verbose)