import random
from apc.utils import update_float, update_uint, format_key
from deca.ff_adf import Adf, AdfValue
from apc import config
from rich import print
from apc.adf import ParsedAdfFile, load_reserve
from apc.config import get_animal_fur_by_seed
from apc.utils import format_key

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

class Animal:
   def __init__(self, details: AdfValue) -> None:
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

def reserve_keys() -> list:
  return list(dict.keys(config.RESERVES))

def reserves(include_keys = False) -> list:
   keys = reserve_keys()
   return [f"{config.RESERVES[r]['name']}{' (' + r + ')' if include_keys else ''}" for r in keys]

def species(reserve_name: str, include_keys = False) -> list:
   species_keys = config.RESERVES[reserve_name]["species"]
   return [f"{format_key(s)}{' (' + s + ')' if include_keys else ''}" for s in species_keys]

def _get_populations(reserve_details: Adf) -> list:
  populations = reserve_details.table_instance_full_values[0].value["Populations"].value
  return [p for p in populations if len(p.value["Groups"].value) > 0]

def _find_animal_level(weight: float, levels: list) -> int:
  level = 0
  for value_i, value in enumerate(levels):
    low_bound, high_bound = value
    if weight <= high_bound and weight > low_bound:
      level = value_i + 1
  return level

def describe_animals(reserve_name: str, species: str, reserve_details: Adf, good = False, verbose = False) -> list:
    populations = _get_populations(reserve_details)
    population = populations[config.RESERVES[reserve_name]["species"].index(species)]
    groups = population.value["Groups"].value
    
    if verbose:
      print(f"processing {format_key(species)} animals...")

    rows = []

    known_species = config.valid_species(species)
    diamond_config = config.ANIMALS[species]["diamonds"]
    diamond_weight = diamond_config["weight_low"] if known_species else config.HIGH_NUMBER
    diamond_score = diamond_config["score_low"] if known_species else config.HIGH_NUMBER
    diamond_levels = diamond_config["levels"] if known_species else []

    if verbose and diamond_score != config.HIGH_NUMBER:
      print(f"Species: {species}, Diamond Weight: {diamond_weight}, Diamond Score: {diamond_score}")

    for group in groups:
      animals = group.value["Animals"].value

      for animal in animals:
        animal = Animal(animal)
        is_diamond = animal.weight >= diamond_weight and animal.score >= diamond_score
        is_go = animal.go
        level = _find_animal_level(animal.weight, diamond_levels) if not is_go else 10
        level_name = format_key(config.Levels(level).name)
        
        if ((good and (is_diamond or is_go)) or not good):
          rows.append([
            f"{level_name}, {level}",
            "M" if animal.gender is "male" else "F",
            round(animal.weight,3),
            round(animal.score, 3),
            animal.visual_seed,
            get_animal_fur_by_seed(species, animal.gender, animal.visual_seed),
            "yes" if is_diamond else "-",
            "yes" if is_go else "-"
          ])

    rows.sort(key=lambda x: x[2], reverse=True)
    return rows 

def describe_reserve(reserve_name: str, reserve_details: Adf, include_species = True, verbose = False) -> list:
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

      species = config.RESERVES[reserve_name]["species"][population_cnt] if include_species else str(population_cnt)
      known_species = species in config.ANIMALS.keys()
      diamond_weight = config.ANIMALS[species]["diamonds"]["weight_low"] if known_species else config.HIGH_NUMBER
      diamond_score = config.ANIMALS[species]["diamonds"]["score_low"] if known_species else config.HIGH_NUMBER
      species = format_key(species)
      population_cnt += 1

      if verbose and diamond_score != config.HIGH_NUMBER:
        print(f"Species: {species}, Diamond Weight: {diamond_weight}, Diamond Score: {diamond_score}")

      for group in groups:
        animals = group.value["Animals"].value
        group_animal_cnt = len(animals)
        animal_cnt += group_animal_cnt
        total_cnt += group_animal_cnt

        for animal in animals:
          animal = Animal(animal)

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
        species, 
        animal_cnt,
        male_cnt,
        female_cnt,
        round(population_high_weight, 3), 
        round(population_high_score, 3),
        diamond_cnt,
        go_cnt
      ])

    return rows

def _get_males_not_go(groups: list) -> list:
  male_animals = []
  for group in groups:
    animals = group.value["Animals"].value  
    for animal in animals:
      animal = Animal(animal)
      if (animal.gender == "male" and not animal.go):
        male_animals.append(animal)
  return male_animals

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

def _process_all(species_config: dict, groups: list, reserve_data: bytearray, cb: callable, kwargs = {}) -> None:
  male_animals = _get_males_not_go(groups)
  for animal in male_animals:
    cb(animal, species_config, reserve_data, **kwargs)

def _go_all(species: str, groups: list, reserve_data: bytearray) -> None:
  go_config = config.ANIMALS[species]["go"]
  _process_all(go_config, groups, reserve_data, _create_go)

def _diamond_all(species: str, groups: list, reserve_data: bytearray, rares: bool = False) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  _process_all(species_config, groups, reserve_data, _create_diamond, { "rares": rares })

def _process_furs(species_config: dict, furs: list, groups: list, reserve_data: bytearray, cb: callable) -> None:
  male_animals = _get_males_not_go(groups)
  chosen_animals = random.sample(male_animals, k = len(furs))
  for animal_i, animal in enumerate(chosen_animals):
    cb(animal, species_config, reserve_data, fur = furs[animal_i])  

def _go_furs(species: str, groups: list, reserve_data: bytearray) -> None:
  go_config = config.ANIMALS[species]["go"]
  go_furs = _dict_values(go_config["furs"])
  _process_furs(go_config, go_furs, groups, reserve_data, _create_go)

def _diamond_furs(species: str, groups: list, reserve_data: bytearray) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  if "furs" in species_config and "male" in species_config["furs"]:
    diamond_furs = _dict_values(species_config["furs"]["male"])
  else:
    raise Exception("Furs have not been loaded for this species yet.")
  _process_furs(species_config, diamond_furs, groups, reserve_data, _create_diamond)

def _process_some(species_config: dict, groups: list, reserve_data: bytearray, percent: int, cb: callable, kwargs = {}) -> None:
  male_animals = _get_males_not_go(groups)
  animal_cnt = round((percent / 100) * len(male_animals))
  chosen_animals = random.sample(male_animals, k = animal_cnt)
  for animal in chosen_animals:
    cb(animal, species_config, reserve_data, **kwargs)

def _go_some(species: str, groups: list, reserve_data: bytearray, percent: int) -> None:
  go_config = config.ANIMALS[species]["go"]
  _process_some(go_config, groups, reserve_data, percent, _create_go)

def _diamond_some(species: str, groups: list, reserve_data: bytearray, percent: int, rares: bool = False) -> None:
  species_config = config.ANIMALS[species]["diamonds"]
  _process_some(species_config, groups, reserve_data, percent, _create_diamond, { "rares": rares })
  
def mod(reserve_name: str, reserve_details: ParsedAdfFile, species: str, strategy: str, modifier: int = None, rares: bool = False, verbose = False):
  species_details = _species(reserve_name, reserve_details.adf, species)
  groups = species_details.value["Groups"].value
  species_name = format_key(species)
  reserve_data = reserve_details.decompressed.data

  if (strategy == config.Strategy.go_all):
    _go_all(species, groups, reserve_data)
    print(f"[green]All {species_name} males are now Great Ones![/green]")
  elif (strategy == config.Strategy.go_furs):
    _go_furs(species, groups, reserve_data)
    print(f"[green]All {species_name} Great One furs have been added![/green]")
  elif (strategy == config.Strategy.go_some):
    _go_some(species, groups, reserve_data, modifier)
    print(f"[green]All {modifier}% of male {species_name} are now Great Ones![/green]")
  elif (strategy == config.Strategy.diamond_all):
    _diamond_all(species, groups, reserve_data, rares)
    print(f"[green]All {species_name} males are now Diamonds![/green]")  
  elif (strategy == config.Strategy.diamond_furs):
    _diamond_furs(species, groups, reserve_data)
    print(f"[green]All {species_name} males are now Diamonds![/green]")
  elif (strategy == config.Strategy.diamond_some):
    _diamond_some(species, groups, reserve_data, modifier, rares)
    print(f"[green]All {modifier}% of male {species_name} are now Diamonds![/green]")    

  reserve_details.decompressed.save(config.MOD_DIR_PATH, verbose=verbose)
  return describe_reserve(reserve_name, load_reserve(reserve_name, True, verbose=verbose).adf, verbose=verbose)