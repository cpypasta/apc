import random
from apc.utils import update_float, update_uint
from deca.ff_adf import Adf, AdfValue
from apc import config, adf
from rich import print
from apc.adf import ParsedAdfFile, load_reserve
from apc.config import get_animal_fur_by_seed, get_species_name, get_reserve_name, get_level_name, get_reserve, valid_species_for_reserve, format_key
from typing import List

class Animal:
    def __init__(self, details: AdfValue, species: str) -> None:
      gender = "male" if details.value["Gender"].value == 1 else "female"
      self.gender = gender
      self.weight = float(details.value["Weight"].value)
      self.score = float(details.value["Score"].value)
      self.go = details.value["IsGreatOne"].value == 1
      self.visual_seed = details.value["VisualVariationSeed"].value
      self.weight_offset = details.value["Weight"].data_offset
      self.score_offset = details.value["Score"].data_offset
      self.go_offset = details.value["IsGreatOne"].data_offset
      self.visual_seed_offset = details.value["VisualVariationSeed"].data_offset
      self.gender_offset = details.value["Gender"].data_offset
      self.species = species
            
    def __repr__(self) -> str:
      return str({ 
        "species": self.species,
        "gender": self.gender, 
        "weight": self.weight, 
        "score": self.score, 
        "go": self.go, 
        "seed": self.visual_seed,
        "score_offset": self.score_offset
      })
      
class NoAnimalsException(Exception):
  pass
      
def _species(reserve_name: str, reserve_details: Adf, species: str) -> list:
   reserve = config.RESERVES[reserve_name]
   species_index = reserve["species"].index(species)
   populations = _get_populations(reserve_details)
   return populations[species_index]

def _random_float(low: int, high: int, precision: int = 3) -> float:
   return round(random.uniform(low, high), precision)

def _dict_values(dict):
  return list(dict.values())

def _random_choice(choices):
   return random.choice(_dict_values(choices))

def reserve_keys() -> list:
  return list(dict.keys(config.RESERVES))

def reserves(include_keys = False) -> list:
   keys = reserve_keys()
   return [f"{get_reserve_name(r)}{' (' + r + ')' if include_keys else ''}" for r in keys]

def species_key(reserve_name: str, include_keys = False) -> list:
   species_keys = config.RESERVES[reserve_name]["species"]
   return [f"{get_species_name(s)}{' (' + s + ')' if include_keys else ''}" for s in species_keys]

def _get_populations(reserve_details: Adf) -> list:
  populations = reserve_details.table_instance_full_values[0].value["Populations"].value
  return [p for p in populations if len(p.value["Groups"].value) > 0]

def _find_animal_level(weight: float, levels: list) -> int:
  level = 1  
  weight = round(weight) if weight > 1 else round(weight, 3)
  for value_i, value in enumerate(levels):
    low_bound, high_bound = value  
    high_bound = round(high_bound) if high_bound > 1 else round(high_bound, 3)
    if (weight <= high_bound and weight > low_bound) or weight > high_bound:
      level = value_i + 1
  return level

def _is_go(animal: Animal) -> bool:
  return animal.gender == "male" and animal.go

def _is_diamond(animal: Animal) -> bool:
  known_species = config.valid_species(animal.species)
  diamond_config = config.ANIMALS[animal.species]["diamonds"]
  diamond_score = diamond_config["score_low"] if known_species else config.HIGH_NUMBER
  diamond_gender = config.get_diamond_gender(animal.species)
  return animal.score >= diamond_score and (animal.gender == diamond_gender or diamond_gender == "both")

def find_animals(species: str, modded = False, good = False, verbose = False, top: bool = False) -> list:
  reserves = reserve_keys()
  animals = []
  for reserve in reserves:
    if valid_species_for_reserve(species, reserve):
      reserve_details = adf.load_reserve(reserve, modded)
      reserve_animals = describe_animals(reserve, species, reserve_details.adf, good, verbose)
      animals.extend(reserve_animals)  
  animals = sorted(animals, key = lambda x : x[4], reverse=True)
  return animals[:10] if top else animals

def describe_animals(reserve_name: str, species: str, reserve_details: Adf, good = False, verbose = False, top: bool = False) -> list:
    populations = _get_populations(reserve_details)
    population = populations[get_reserve(reserve_name)["species"].index(species)]
    groups = population.value["Groups"].value
    
    if verbose:
      print(f"processing {format_key(species)} animals...")

    rows = []

    known_species = config.valid_species(species)
    diamond_config = config.ANIMALS[species]["diamonds"]
    diamond_weight = diamond_config["weight_low"] if known_species else config.HIGH_NUMBER
    diamond_score = diamond_config["score_low"] if known_species else config.HIGH_NUMBER
    animal_levels = diamond_config["levels"] if known_species else []

    if verbose and diamond_score != config.HIGH_NUMBER:
      print(f"Species: {species}, Diamond Weight: {diamond_weight}, Diamond Score: {diamond_score}")

    for group in groups:
      animals = group.value["Animals"].value

      for animal in animals:
        animal = Animal(animal, species)
        is_diamond = _is_diamond(animal)
        is_go = _is_go(animal)
        
        if ((good and (is_diamond or is_go)) or not good):
          level = _find_animal_level(animal.weight, animal_levels) if not is_go else 10
          level_name = get_level_name(config.Levels(level))          
          rows.append([
            get_reserve_name(reserve_name),
            f"{level_name}, {level}",
            config.MALE if animal.gender == "male" else config.FEMALE,
            round(animal.weight,2),
            round(animal.score, 2),
            animal.visual_seed,
            get_animal_fur_by_seed(species, animal.gender, animal.visual_seed),
            config.YES if is_diamond and not is_go else "-",
            config.YES if is_go else "-"
          ])

    rows.sort(key=lambda x: x[4], reverse=True)
    return rows[:10] if top else rows 

def describe_reserve(reserve_key: str, reserve_details: Adf, include_species = True, verbose = False) -> list:
    populations = _get_populations(reserve_details)

    if verbose:
      print(f"processing {len(populations)} species...")

    rows = []
    total_cnt = 0
    population_cnt = 0
    for population in populations:
      groups = population.value["Groups"].value
      animal_cnt = 0
      population_high_weight = 0        
      population_high_score = 0
      female_cnt = 0
      male_cnt = 0
      go_cnt = 0
      diamond_cnt = 0

      species_key = config.RESERVES[reserve_key]["species"][population_cnt] if include_species else str(population_cnt)
      known_species = species_key in config.ANIMALS.keys()
      diamond_weight = config.ANIMALS[species_key]["diamonds"]["weight_low"] if known_species else config.HIGH_NUMBER
      diamond_score = config.ANIMALS[species_key]["diamonds"]["score_low"] if known_species else config.HIGH_NUMBER
      species_name = config.get_reserve_species_name(species_key, reserve_key)
      population_cnt += 1

      if verbose and diamond_score != config.HIGH_NUMBER:
        print(f"Species: {species_name}, Diamond Weight: {diamond_weight}, Diamond Score: {diamond_score}")

      for group in groups:
        animals = group.value["Animals"].value
        group_animal_cnt = len(animals)
        animal_cnt += group_animal_cnt
        total_cnt += group_animal_cnt

        for animal in animals:
          animal = Animal(animal, species_key)

          if animal.gender == "male":
            male_cnt += 1
            if animal.score > population_high_score:
                population_high_score = animal.score                  
          else:
            female_cnt += 1

          if animal.weight > population_high_weight:
              population_high_weight = animal.weight

          if animal.go:
            go_cnt += 1
          elif animal.weight >= diamond_weight and animal.score >= diamond_score:
            diamond_cnt += 1

      rows.append([
        species_name, 
        animal_cnt,
        male_cnt,
        female_cnt,
        round(population_high_weight, 2), 
        round(population_high_score, 2),
        diamond_cnt,
        go_cnt
      ])

    return rows

def _get_eligible_animals(groups: list, species: str, gender: str = "male") -> list:
  eligible_animals = []
  for group in groups:
    animals = group.value["Animals"].value  
    for animal in animals:
      animal = Animal(animal, species)
      if (not (_is_diamond(animal) or _is_go(animal))):
        if animal.gender == gender or gender == "both":
          eligible_animals.append(animal)
  return eligible_animals

def _create_go(animal: Animal, go_config: dict, data: bytearray, fur: int = None) -> None:
  new_weight = _random_float(go_config["weight_low"], go_config["weight_high"])
  new_score = _random_float(go_config["score_low"], go_config["score_high"])
  visual_seed = fur if fur else _random_choice(go_config["furs"])
  update_float(data, animal.weight_offset, new_weight)
  update_float(data, animal.score_offset, new_score)
  update_uint(data, animal.go_offset, 1)
  update_uint(data, animal.visual_seed_offset, visual_seed) 

def _create_diamond(animal: Animal, species_config: dict, data: bytearray, rares: bool = False, fur: int = None) -> None:
  new_weight = _random_float(species_config["weight_low"], species_config["weight_high"])
  new_score = _random_float(species_config["score_low"], species_config["score_high"])
  visual_seed = None
  if fur:
    visual_seed = fur
  elif "furs" in species_config and animal.gender in species_config["furs"]:
    visual_seed = _random_choice(species_config["furs"][animal.gender])
  update_float(data, animal.weight_offset, new_weight)
  update_float(data, animal.score_offset, new_score)
  if visual_seed and (rares or fur):
    update_uint(data, animal.visual_seed_offset, visual_seed)

def _create_fur(animal: Animal, species_config: dict, data: bytearray, fur: int = None) -> None:
  visual_seed = None
  if fur:
    visual_seed = fur
  elif "furs" in species_config and animal.gender in species_config["furs"]:
    visual_seed = _random_choice(species_config["furs"][animal.gender])  
  update_uint(data, animal.visual_seed_offset, visual_seed)

def _create_male(animal: Animal, _config: dict, data: bytearray) -> None:
  update_uint(data, animal.gender_offset, 1)
  
def _create_female(animal: Animal, _config: dict, data: bytearray) -> None:
  update_uint(data, animal.gender_offset, 2)

def _process_all(species: str, species_config: dict, groups: list, reserve_data: bytearray, cb: callable, kwargs = {}, gender: str = "male") -> None:
  animals = _get_eligible_animals(groups, species, gender=gender)
  if len(animals) == 0:
    raise NoAnimalsException(f"There are not enough {get_species_name(species)} to process")  
  for animal in animals:
    cb(animal, species_config, reserve_data, **kwargs)

def _go_all(species: str, groups: list, reserve_data: bytearray) -> None:
  go_config = config.ANIMALS[species]["go"]
  _process_all(species, go_config, groups, reserve_data, _create_go)

def _diamond_all(species: str, groups: list, reserve_data: bytearray, rares: bool = False) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  diamond_gender = config.get_diamond_gender(species)
  _process_all(species, species_config, groups, reserve_data, _create_diamond, { "rares": rares }, gender=diamond_gender)

def diamond_test_seed(species: str, groups: list, data: bytearray, seed: int, gender: int = 1) -> None:
  eligible_animals = []
  for group in groups:
    animals = group.value["Animals"].value  
    for animal in animals:
      animal = Animal(animal, species)
      eligible_animals.append(animal)
        
  for animal in eligible_animals:
    update_float(data, animal.weight_offset, seed)
    update_float(data, animal.score_offset, seed / 10000)
    update_uint(data, animal.visual_seed_offset, seed)
    update_uint(data, animal.gender_offset, gender)
    seed += 1
  return seed

def diamond_test_seeds(species: str, groups: list, data: bytearray, seeds: List[int]) -> None:
  eligible_animals = []
  for group in groups:
    animals = group.value["Animals"].value  
    for animal in animals[:len(seeds)]:
      animal = Animal(animal, species)
      eligible_animals.append(animal)
        
  for animal_i, animal in enumerate(eligible_animals[:len(seeds)]):
    seed = seeds[animal_i]
    update_float(data, animal.weight_offset, seed)
    update_float(data, animal.score_offset, seed / 10000)
    update_uint(data, animal.visual_seed_offset, seed)
    update_uint(data, animal.gender_offset, 1)
    seed += 1
  return seed

def _process_furs(species, species_config: dict, furs: list, groups: list, reserve_data: bytearray, cb: callable, gender: str = "male") -> None:
  eligible_animals = _get_eligible_animals(groups, species, gender=gender) 
  if len(eligible_animals) == 0:
    raise NoAnimalsException(f"There are not enough {get_species_name(species)} to process") 
  chosen_animals = random.sample(eligible_animals, k = len(furs))
  for animal_i, animal in enumerate(chosen_animals):
    cb(animal, species_config, reserve_data, fur = furs[animal_i])  

def _go_furs(species: str, groups: list, reserve_data: bytearray) -> None:
  go_config = config.ANIMALS[species]["go"]
  go_furs = _dict_values(go_config["furs"])
  _process_furs(species, go_config, go_furs, groups, reserve_data, _create_go)

def _diamond_furs(species: str, groups: list, reserve_data: bytearray) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  diamond_gender = config.get_diamond_gender(species)
  if "furs" in species_config and diamond_gender in species_config["furs"]:
    diamond_furs = _dict_values(species_config["furs"][diamond_gender])
  else:
    raise Exception("Furs have not been loaded for this species yet.")
  _process_furs(species, species_config, diamond_furs, groups, reserve_data, _create_diamond, gender=diamond_gender)

def _furs(species: str, groups: list, reserve_data: bytearray) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  male_furs = config.get_species_furs(species, "male")
  female_furs = config.get_species_furs(species, "female")
  _process_furs(species, species_config, male_furs, groups, reserve_data, _create_fur, gender="male")
  _process_furs(species, species_config, female_furs, groups, reserve_data, _create_fur, gender="female")

def _process_some(species, species_config: dict, groups: list, reserve_data: bytearray, modifier: int, percentage: bool, cb: callable, kwargs: dict = {}, gender: str = "male") -> None:
  eligible_animals = _get_eligible_animals(groups, species, gender=gender)
  if len(eligible_animals) == 0:
    raise NoAnimalsException(f"There are not enough {get_species_name(species)} to process")
  if percentage:
    animal_cnt = round((modifier / 100) * len(eligible_animals))
  else:
    animal_cnt = modifier
  chosen_animals = random.sample(eligible_animals, k = animal_cnt)
  for animal in chosen_animals:
    cb(animal, species_config, reserve_data, **kwargs)

def _go_some(species: str, groups: list, reserve_data: bytearray, modifier: int = None, percentage: bool = False) -> None:
  go_config = config.ANIMALS[species]["go"]
  _process_some(species, go_config, groups, reserve_data, modifier, percentage, _create_go)

def _diamond_some(species: str, groups: list, reserve_data: bytearray, modifier: int = None, percentage: bool = False, rares: bool = False) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  diamond_gender = config.get_diamond_gender(species)
  _process_some(species, species_config, groups, reserve_data, modifier, percentage, _create_diamond, { "rares": rares }, gender=diamond_gender)

def _furs_some(species: str, groups: list, reserve_data: bytearray, modifier: int = None, percentage: bool = False) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  _process_some(species, species_config, groups, reserve_data, modifier, percentage, _create_fur, gender="both")

def _male_some(species: str, groups: list, reserve_data: bytearray, modifier: int = None, percentage: bool = False) -> None:
  _process_some(species, {}, groups, reserve_data, modifier, percentage, _create_male, gender = "female")  
  
def _female_some(species: str, groups: list, reserve_data: bytearray, modifier: int = None, percentage: bool = False) -> None:
  _process_some(species, {}, groups, reserve_data, modifier, percentage, _create_female, gender = "male")  
  
def mod(reserve_name: str, reserve_details: ParsedAdfFile, species: str, strategy: str, modifier: int = None, percentage: bool = False, rares: bool = False, verbose = False):
  species_details = _species(reserve_name, reserve_details.adf, species)
  groups = species_details.value["Groups"].value
  species_name = format_key(species)
  reserve_data = reserve_details.decompressed.data

  if (strategy == config.Strategy.go_all):
    _go_all(species, groups, reserve_data)
    print(f"[green]All {species_name} are now Great Ones![/green]")
  elif (strategy == config.Strategy.go_furs):
    _go_furs(species, groups, reserve_data)
    print(f"[green]All {species_name} Great One furs have been added![/green]")
  elif (strategy == config.Strategy.go_some):
    _go_some(species, groups, reserve_data, modifier, percentage)
    print(f"[green]All {modifier}{'%' if percentage else ''} {species_name} are now Great Ones![/green]")
  elif (strategy == config.Strategy.diamond_all):
    _diamond_all(species, groups, reserve_data, rares)
    print(f"[green]All {species_name} are now Diamonds![/green]")  
  elif (strategy == config.Strategy.diamond_furs):
    _diamond_furs(species, groups, reserve_data)
    print(f"[green]All {species_name} are now Diamonds![/green]")
  elif (strategy == config.Strategy.diamond_some):
    _diamond_some(species, groups, reserve_data, modifier, percentage, rares)
    print(f"[green]All {modifier}{'%' if percentage else ''} {species_name} are now Diamonds![/green]")  
  elif (strategy == config.Strategy.males):
    _male_some(species, groups, reserve_data, modifier, percentage)
    print(f"[green]All {modifier}{'%' if percentage else ''} {species_name} are now males![/green]")  
  elif (strategy == config.Strategy.females):
    _female_some(species, groups, reserve_data, modifier, percentage)
    print(f"[green]All {modifier}{'%' if percentage else ''} {species_name} are now females![/green]") 
  elif (strategy == config.Strategy.furs):
    _furs(species, groups, reserve_data)
    print(f"[green]All {modifier}{'%' if percentage else ''} {species_name} are now random furs![/green]") 
  elif (strategy == config.Strategy.furs_some):
    _furs_some(species, groups, reserve_data, modifier, percentage)
    print(f"[green]All {modifier}{'%' if percentage else ''} {species_name} are now random furs![/green]") 
  else:
    print(f"[red]Unknown strategy: {strategy}")  

  reserve_details.decompressed.save(config.MOD_DIR_PATH, verbose=verbose)
  return describe_reserve(reserve_name, load_reserve(reserve_name, True, verbose=verbose).adf, verbose=verbose)