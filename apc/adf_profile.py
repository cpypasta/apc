import struct, json, re
from pathlib import Path
from typing import Tuple, List

typedef_s8 = 1477249634
typedef_u8 = 211976733
typedef_s16 = 3510620051
typedef_u16 = 2261865149
typedef_s32 = 422569523
typedef_u32 = 123620943
typedef_s64 = 2940286287
typedef_u64 = 2704924703
typedef_f32 = 1964352007
typedef_f64 = 3322541667
PRIMITIVES = [typedef_s8, typedef_u8, typedef_s16, typedef_u16, typedef_s32, typedef_u32, typedef_s64, typedef_u64, typedef_f32, typedef_f64]
PRIMITIVE_1 = [typedef_s8, typedef_u8]
PRIMITIVE_2 = [typedef_s16, typedef_u16]
PRIMITIVE_8 = [typedef_s64, typedef_u64, typedef_f64]
STRUCTURE = 1
ARRAY = 3

class AdfArray:
  def __init__(self, name: str, population: int, group: int, length: int, header_start_offset: int, header_length_offset: int, header_array_offset: int, array_start_offset: int, array_end_offset: int, rel_array_start_offset: int, rel_array_end_offset: int, male_indices: List[int], female_indices: List[int]) -> None:
    self.name = name
    self.population = population
    self.group = group
    self.length = length
    self.header_start_offset = header_start_offset
    self.header_length_offset = header_length_offset
    self.header_array_offset = header_array_offset
    self.array_org_start_offset = array_start_offset
    self.array_org_end_offset = array_end_offset
    self.array_start_offset = array_start_offset
    self.array_end_offset = array_end_offset
    self.rel_array_start_offset = rel_array_start_offset
    self.rel_array_end_offset = rel_array_end_offset
    self.male_indices = male_indices
    self.female_indices = female_indices
    self.male_cnt = len(male_indices) if male_indices else 0
    self.female_cnt = len(female_indices) if female_indices else 0
    
  def __repr__(self) -> str:
    return f"{self.name} ; Header Offset: {self.header_start_offset},{hex(self.header_start_offset)}; Data Offset: {self.array_start_offset},{hex(self.array_start_offset)}"

class Animal:
  def __init__(self, gender: str, weight: float, score: float, is_great_one: bool, visual_variation_seed: int) -> None:
    self.gender = 1 if gender == "male" else 2
    self.weight = weight
    self.score = score
    self.is_great_one = 1 if is_great_one else 0
    self.visual_variation_seed = visual_variation_seed
    self.id = 0
    self.map_position_x = 0.0
    self.map_position_y = 0.0
    self.size = len(self.to_bytes())
    
  def __repr__(self) -> str:
    return f"""
      gender: {self.gender},{create_u8(self.gender)},
      weight: {self.weight},{create_f32(self.weight)},
      score: {self.score},{create_f32(self.score)},
      is_great_one: {self.is_great_one},{create_u8(self.is_great_one)},
      seed: {self.visual_variation_seed},{create_u32(self.visual_variation_seed)},
      id: {self.id},{create_u32(self.id)},
      x: {self.map_position_x},{create_f32(self.map_position_x)},
      y: {self.map_position_y},{create_f32(self.map_position_y)}
    """
    
  def to_bytes(self) -> bytearray:
    gender = create_u8(self.gender)
    weight = create_f32(self.weight)
    score = create_f32(self.score)
    is_great_one = create_u8(self.is_great_one)
    visual_variation_seed = create_u32(self.visual_variation_seed)
    id = create_u32(self.id)
    map_position_x = create_f32(self.map_position_x)
    map_position_y = create_f32(self.map_position_y)
    return gender+weight+score+is_great_one+visual_variation_seed+id+map_position_x+map_position_y


def read_u32(data: bytearray) -> int:
  return struct.unpack("I", data)[0]

def create_u32(value: int) -> bytearray:
  return bytearray(struct.pack("I", value))

def read_u8(data: bytearray) -> int:
  return struct.unpack("B", data)[0]

def create_u8(value: int) -> bytearray:
  return bytearray(struct.pack("B0I", value))

def create_f32(value: float) -> bytearray:
  return bytearray(struct.pack("f", value))

def read_u64(data: bytearray) -> int:
  return struct.unpack("Q", data)[0]

def read_str(data: bytearray) -> str:
  value = data[0:-1]
  return value.decode("utf-8")

def write_value(data: bytearray, new_data: bytearray, offset: int) -> None:
  data[offset:offset+len(new_data)] = new_data

def find_length_of_string(data: bytearray) -> bytearray:
  for i in range(len(data)):
    if data[i:i+1] == b'\00':
      return i
  return 0

def find_nametable_size(data: bytearray, count: int) -> int:
  size = 0
  eos = 1
  for i in range(count):
    i_length = read_u8(data[i:i+1])
    size += 1 + i_length + eos
  return size

def read_nametables(data: bytearray, count: int) -> List[str]:
  nametable_sizes = []
  nametables = []
  for i in range(count):
    i_length = read_u8(data[i:i+1])
    nametable_sizes.append(i_length)
  
  table_offset = count
  pointer = table_offset
  
  for i in range(count):
    i_length = nametable_sizes[i]
    nametables.append(read_str(data[pointer:pointer+i_length+1]))
    pointer += i_length + 1
  
  return nametables

def read_typemember(data: bytearray, nametables: List[str]) -> dict:
  name_index = read_u64(data[0:8]) 
  name = nametables[name_index]
  type_hash = read_u32(data[8:12])
  size = read_u32(data[12:16])
  offset = read_u32(data[16:20])
  return {
    "name": name,
    "type_hash": type_hash,
    "size": size,
    "offset": offset
  }

def read_typedef(header: bytearray, offset: int, nametables: List[str]) -> Tuple[int, dict]:
  header_size = 36
  member_size = 32
  metatype = read_u32(header[0:4])
  size = read_u32(header[4:8])
  type_hash = read_u32(header[12:16])
  name_index = read_u64(header[16:24])
  element_type_hash = read_u32(header[28:32])
  name = nametables[name_index]
  
  if metatype == 1:
    member_count = read_u32(header[header_size:header_size+4])
    structure_size = header_size + 4 + (member_size * member_count)
    members = []
    for i in range(member_count):
      pointer = i * member_size
      members.append(read_typemember(header[header_size+4+pointer:], nametables))
    return (structure_size, {
      "name": name, 
      "metatype": metatype,
      "type_hash": type_hash,
      "start": offset, 
      "end": offset + structure_size,
      "size": size,
      "members": members
    })
  elif metatype == 0:
    return (header_size, {
      "name": name, 
      "metatype": metatype,
      "type_hash": type_hash,
      "start": offset, 
      "end": offset + header_size
    })
  else:
    return (header_size+4, {
      "name": name, 
      "metatype": metatype,
      "type_hash": type_hash,
      "element_type_hash": element_type_hash,
      "start": offset, 
      "end": offset+header_size+4
    })

def find_typedef_offset(data: bytearray, typedef_offset: int, count: int, nametables: List[str]) -> dict:
  pointer = typedef_offset
  offsets = []
  for i in range(count):
    read_size, info = read_typedef(data[pointer:], pointer, nametables)
    pointer += read_size
    offsets.append(info)
  
  type_map = {}
  for offset in offsets:
    type_map[offset["type_hash"]] = { 
      "name": offset["name"], 
      "metatype": offset["metatype"],
      "size": offset["size"] if "size" in offset else None,
      "element_type_hash": offset["element_type_hash"] if "element_type_hash" in offset else None,
      "members": offset["members"] if "members" in offset else []
    }
  
  return {
    "start": typedef_offset,
    "end": pointer,
    "offsets": offsets,
    "type_map": type_map
  }

def get_primitive_size(type_id: int) -> int:
  if type_id in PRIMITIVE_1:
    return 1
  elif type_id in PRIMITIVE_2:
    return 2
  elif type_id in PRIMITIVE_8:
    return 8
  else:
    return 4

def read_instance(data: bytearray, offset: int, pointer: int, type_id: int, type_map: dict) -> dict:
  value = None
  pos = offset+pointer
  
  if type_id in PRIMITIVES:
    primitive_size = get_primitive_size(type_id)
    value = f"Primitive ({primitive_size}, {pos})"
    pointer += primitive_size
  else:
    type_def = type_map[type_id]
    if type_def["metatype"] == STRUCTURE:
      value = {}
      value["structure_offset"] = (pos, pos+type_def["size"])
      org_pointer = pointer
      for m in type_def["members"]:
        m_offset = m["offset"]
        pointer = org_pointer + m_offset
        v = read_instance(data, offset, pointer, int(m["type_hash"]), type_map)
        value[m["name"]] = { 
          "value": v[0]
        }
      pointer = org_pointer + type_def["size"]
    elif type_def["metatype"] == ARRAY:
      array_offset = read_u32(data[pos:pos+4])
      flags = read_u32(data[pos+4:pos+8])
      length = read_u32(data[pos+8:pos+12]) 
      array_header_size = 12
      org_pos = pos
      pointer += array_header_size
      org_pointer = pointer
      pos = offset+pointer
      value = { "Array": { 
        "name": type_def["name"], 
        "header_offset": (org_pos, org_pos+array_header_size),
        "flags": flags,
        "length": length
      }}
      pointer = array_offset
      
      if length > 0:
        element_type = type_def["element_type_hash"]
        new_pointer = pointer
        values = []
        for i in range(length):
          v, new_pointer = read_instance(data, offset, new_pointer, int(element_type), type_map)
          values.append(v)
        value["Array"]["type"] = "Primitives" if element_type in PRIMITIVES else "Structures"
        value["Array"]["array_offset"] = (offset+pointer, offset+new_pointer)
        value["Array"]["values"] = values
      
      pointer = org_pointer
    else:
      print(f"Unknown metatype: {type_def['metatype']}")
  
  return (value, pointer)

def find_instance_offset(data: bytearray, offset: int, count: int, nametables: List[str], type_map: dict) -> dict:
  instance_header_size = 24
  instances = []
  for i in range(count):
    pointer = offset + i * count
    instance_type = read_u32(data[pointer+4:pointer+8])
    instance_offset = read_u32(data[pointer+8:pointer+12])
    instance_size = read_u32(data[pointer+12:pointer+16])
    instance_name = nametables[read_u64(data[pointer+16:pointer+24])]
    instances.append({ 
      "offset": (instance_offset, instance_offset + instance_size), 
      "size": instance_size, 
      f"{instance_name}": read_instance(data, instance_offset, 0, instance_type, type_map)[0]
    })
  
  return {
    "offset": (offset, offset + count*instance_header_size),
    "instances": instances
  }
  
def find_population_array_offsets(offsets: dict, result: List[dict] = [], org_path: str = "", prev_key: str = "", index: int = 0) -> List[dict]:
  for key, v in offsets.items():
    if org_path == "":
      path = ""
    else:
      path = org_path
    if isinstance(v, dict):
      if prev_key != "":
        path += f"{prev_key}[{index}];"
      value = v["value"]
      if isinstance(v, dict) and "Array" in value:
        array_details = value["Array"]
        result.append({
          "path": path,
          "key": key,
          "name": array_details["name"],
          "index": index,
          "length": array_details["length"],
          "header": array_details["header_offset"],
          "values": array_details["array_offset"] if "array_offset" in array_details else None
        })
                
        if "values" in array_details:
          array_values = array_details["values"]
          if len(array_values) > 0 and isinstance(array_values[0], dict):
            for i, value in enumerate(array_details["values"]):
              find_population_array_offsets(value, result, path, key, i)
  return result

def parse_gender_cnt(data: bytearray, length: int, data_offset: int) -> dict:
  male_indices = []
  female_indices = []
  for i in range(length):
    animal_offset = data_offset+i*32
    gender = read_u32(data[animal_offset:animal_offset+4])
    if gender == 1:
      male_indices.append(i)
    else:
      female_indices.append(i)
  return (male_indices, female_indices)

def create_array(offset: dict, instance_offset: int, data: bytearray = None, population: int = 0, group: int = 0) -> AdfArray:
  header_start_offset = offset["header"][0]
  value_start_offset, value_end_offset = offset["values"] if offset["values"] else (0,0)
  if data:
    male_indices, female_indices = parse_gender_cnt(data, offset["length"], value_start_offset)
  else:
    male_indices = None
    female_indices = None
  return AdfArray(
    f"{offset['path']}{offset['key']};{offset['name']}",
    int(population), 
    int(group), 
    offset["length"], 
    header_start_offset, 
    header_start_offset+8, 
    header_start_offset, 
    value_start_offset, 
    value_end_offset,
    value_start_offset-instance_offset, 
    value_end_offset-instance_offset,
    male_indices,
    female_indices
  )  

def create_animal_array(offset: dict, instance_offset: int, data: bytearray) -> AdfArray:
  population, group = re.findall(r'\d+', offset["path"])
  return create_array(offset, instance_offset, data, population, group)

def profile_header(data: bytearray) -> dict:
  header = data[:64]
  instance_count = read_u32(header[8:12])
  instance_offset = read_u32(header[12:16])
  typedef_count = read_u32(header[16:20])
  typedef_offset = read_u32(header[20:24])
  stringhash_offset = read_u32(header[28:32])
  nametable_count = read_u32(header[32:36])
  nametable_offset = read_u32(header[36:40])
  total_size = read_u32(header[40:44])  
  
  return {
    "total_size": total_size,
    "typedef_count": typedef_count,
    "typedef_offset": typedef_offset,
    "nametable_count": nametable_count,
    "nametable_offset": nametable_offset,
    "instance_count": instance_count,
    "instance_offset": instance_offset,
    "stringhash_offset": stringhash_offset,
    "header_start": 0,
    "header_instance_offset": 12,
    "header_typedef_offset": 20,
    "header_stringhash_offset": 28,
    "header_nametable_offset": 36,
    "header_total_size_offset": 40,
    "header_end": 64
  }  

def create_profile(filename: Path) -> None:
  data = bytearray(filename.read_bytes())
  header_profile = profile_header(data)
  instance_count = header_profile["instance_count"]
  instance_offset = header_profile["instance_offset"]
  typedef_count = header_profile["typedef_count"]
  typedef_offset = header_profile["typedef_offset"]
  nametable_count = header_profile["nametable_count"]
  nametable_offset = header_profile["nametable_offset"]
  total_size = header_profile["total_size"]
  comment_size = find_length_of_string(data[64:])
  nametable_size = find_nametable_size(data[nametable_offset:], nametable_count)
  nametables = read_nametables(data[nametable_offset:], nametable_count)
  typedef_offsets = find_typedef_offset(data, typedef_offset, typedef_count, nametables)
  type_map = typedef_offsets["type_map"]
  instance_offsets = find_instance_offset(data, instance_offset, instance_count, nametables, type_map)
  
  return {
    "total_size": total_size,
    "header_start": 0,
    "header_instance_offset": 12,
    "header_typedef_offset": 20,
    "header_stringhash_offset": 28,
    "header_nametable_offset": 36,
    "header_total_size_offset": 40,
    "header_end": 64,
    "comment_start": 64,
    "comment_end": 64 + comment_size,
    "instance_start": instance_offsets["instances"][0]["offset"][0],
    "instance_end": instance_offsets["instances"][0]["offset"][0] + instance_offsets["instances"][0]["size"],
    "instance_header_start": instance_offsets["offset"][0],
    "instance_header_end": instance_offsets["offset"][1],    
    "typedef_start": typedef_offset,
    "typedef_end": typedef_offsets["end"],    
    "nametable_start": nametable_offset,
    "nametable_end": nametable_offset+nametable_size,
    "details": {
      "instance_offsets": instance_offsets
    }
  }
  
def find_arrays(profile: dict, data: bytearray) -> Tuple[List[AdfArray], List[AdfArray]]:
  instance_offsets = profile["details"]["instance_offsets"]
  instance_offset = instance_offsets["instances"][0]["offset"][0]
  array_offsets = find_population_array_offsets(instance_offsets["instances"][0]["0"], [])
  animal_arrays = [create_animal_array(x, instance_offset, data) for x in array_offsets if x["key"] == 'Animals']
  other_arrays = [create_array(x, instance_offset) for x in array_offsets if x["key"] != 'Animals']
  return (animal_arrays, other_arrays)
