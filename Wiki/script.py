import os
import json

def extract_spawn_data(pokemon_name, spawn_folder):
    spawn_path = os.path.join(spawn_folder, f"{pokemon_name}.json")

    if os.path.exists(spawn_path):
        with open(spawn_path, "r") as json_file:
            spawn_data = json.load(json_file)
            return spawn_data.get("spawns", [])
    else:
        return []
#TO DO: Form stats, Bumblezone individual biome support instead of tags, better name handling of spawn jsons so don't have to rename the jsons
#For me: php maintenance/importTextFiles.php --overwrite --use-timestamp ImportPages/*.txt
def format_item_name(item):
    # Grab the text after the colon (ie cobblemon:, then replace underscores with spaces
    return item.split(":")[-1].replace("_", " ").title()

def capitalize_first_letter(s):
    # Capitalize the first letter of words
    return s[0].upper() + s[1:]

def create_txt_file(pokemon_data, spawn_folder, output_folder, pokemon_map, en_us_path):
    # Make the text file in Pages folder
    # NOTICE!!! This WILL fail for Flabebe and Type:Null on freshly obtained species jsons. Edit their names to remove the special e and the colon
    pokemon_name = pokemon_data.get("name", "Error")
    ndex = str(pokemon_data.get('nationalPokedexNumber', 'Error')).zfill(3)  # Prefix with 0's if needed
    
    txt_file_path = os.path.join(output_folder, f"{pokemon_name}.txt")


    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        # Write NextPrev section, subtract 1 from current page & add one
        # NOTICE!!! This will fail for Bulbasaur and whatever is the current newest pokemon, needs manual intervention
        dexprev = str(int(ndex) - 1).zfill(3) if int(ndex) > 1 else ""
        dexnext = str(int(ndex) + 1).zfill(3)

        # Get previous and next Pokemon's name based on dexprev and dexnext numbers from the Dex.txt file
        prev_pokemon_name = pokemon_map.get(dexprev, "")
        next_pokemon_name = pokemon_map.get(dexnext, "")

        txt_file.write(f"{{{{NextPrev|dexprev={dexprev}|prev={prev_pokemon_name}|dexnext={dexnext}|next={next_pokemon_name}}}}}\n\n")

        # Write PokeInfo section
        txt_file.write("{{PokeInfo\n")
        txt_file.write(f"|name={pokemon_name}\n")
        txt_file.write(f"|ndex={ndex}\n")
        txt_file.write(f"|type1={pokemon_data.get('primaryType', '').capitalize()}\n")
        # secondary_type = pokemon_data.get('secondaryType').capitalize()
        if {pokemon_data.get('secondaryType', '').capitalize()} is not None:
            txt_file.write(f"|type2={pokemon_data.get('secondaryType', '').capitalize()}\n")
        abilities = pokemon_data.get('abilities', [])
        regular_abilities = []
        hidden_ability = None
        # Fix the order of ability 1 & 2
        if len(abilities) >= 2:
            ability1 = abilities[0]
            ability2 = abilities[1]
        else:
            ability1 = abilities[0]
            ability2 = None
        
        # Separate abilities into normal and hidden. Assume ability 2 is hidden if ability2 is blank. Another check later for if Poke only has 1 ability
        for ability in abilities:
            if ability.startswith('h:'):
                hidden_ability = ability[2:]
            else:
                regular_abilities.append(ability)
        
        # Get abilitt names from en_us.json
        with open(en_us_path, "r") as en_us_file:
            en_us_data = json.load(en_us_file)
            abilities_dict = en_us_data.get("cobblemon.ability", {})

        # Replace ability names with their proper names
        for i, ability in enumerate(regular_abilities):
            regular_abilities[i] = abilities_dict.get(ability.lower(), ability).title()
        #Check if no hidden ability and no secondary ability aka only has 1 ability
        if hidden_ability is not None:
            hidden_ability = abilities_dict.get(hidden_ability.lower(), hidden_ability).title()

        # Write normal abilities
        unique_regular_abilities = set(regular_abilities)
        # I can't seem to get a new line working here right, but it works either way
        txt_file.write(f"|ability1={'|ability2='.join(unique_regular_abilities) if unique_regular_abilities else ''}\n")
        
        # Write hidden ability if available
        if hidden_ability and hidden_ability != unique_regular_abilities and hidden_ability not in unique_regular_abilities:
            # Check if there are only two abilities
            if len(abilities) == 2:
                txt_file.write("\n|ability2=\n")
#            else:
#                txt_file.write(f"|ability2={hidden_ability}\n")
        
        # Write hidden ability
        txt_file.write(f"|abilityH={hidden_ability if hidden_ability else ''}\n")

        




        # Adjust the gender ratio since cobblemon uses 1.0 as 100%
        male_ratio = pokemon_data.get('maleRatio', 0) * 100  # Multiply by 100 to adjust
        if male_ratio == -100:
            gender_ratio = ""
        else:
            gender_ratio = str(male_ratio)
        # txt_file.write(f"|genderm={gender_ratio}\n")
        # This is probably for Rockruff since it has 4 abilities
        txt_file.write(f"|abilityS=\n")
        txt_file.write(f"|genderm={gender_ratio}\n")
        txt_file.write(f"|catchrate={pokemon_data.get('catchRate', 'Unknown')}\n")

        # Adjusting the height
        height = pokemon_data.get('height', 'Unknown')
        if height != 'Unknown':
            height_decimal = float(height) / 10  # Add one decimal place
        else:
            height_decimal = height
        txt_file.write(f"|height-m={height_decimal}\n")

        # Adjusting the weight
        weight = pokemon_data.get('weight', 'Unknown')
        if weight != 'Unknown':
            weight_decimal = float(weight) / 10  # Add one decimal place
        else:
            weight_decimal = weight
        txt_file.write(f"|weight-kg={weight_decimal}\n")
        egg_groups = pokemon_data.get('eggGroups', [])
        
        # Fix Human-Like
        egg_groups = [group.replace('human_like', 'Human-Like') for group in egg_groups]
        
        if egg_groups:
            egg_group1 = egg_groups[0].title()
            egg_group2 = egg_groups[1].title() if len(egg_groups) > 1 else ''
        else:
            egg_group1 = 'Undiscovered'
            egg_group2 = ''
        
        txt_file.write(f"|eggGroup1={egg_group1}\n")
        txt_file.write(f"|eggGroup2={egg_group2}\n")


        txt_file.write(f"|steps={pokemon_data.get('eggCycles', 'Unknown')}\n")
        ev_yield = pokemon_data.get("evYield", {})
        txt_file.write(f"|evHp={ev_yield.get('hp', 'Unknown')}\n")
        txt_file.write(f"|evAtk={ev_yield.get('attack', 'Unknown')}\n")
        txt_file.write(f"|evDef={ev_yield.get('defence', 'Unknown')}\n")
        txt_file.write(f"|evSa={ev_yield.get('special_attack', 'Unknown')}\n")
        txt_file.write(f"|evSd={ev_yield.get('special_defence', 'Unknown')}\n")
        txt_file.write(f"|evSpe={ev_yield.get('speed', 'Unknown')}\n")
        # Handling forms. We need to eventually add base stats and such for forms but some other time.
        forms = pokemon_data.get('forms', [])
        form_names = [form.get('name') for form in forms]
        form_str = ', '.join(form_names) if form_names else ''
        txt_file.write(f"|form={form_str}\n")
        txt_file.write(f"|alt1=\n|alt1dex=\n")

        # Get dexentry from en_us file
        # NOTICE!!! Script fails with a freshly pulled en_us. They use a special character version of "" for quotes in dex entries. These need searched for and removed first. Can add a python module for special character support but easier to just yeet the special characters
        dex_file_path = r"C:\Users\changeme\Documents\WikiArchive\Wiki\en_us.json"
        with open(dex_file_path, "r") as dex_file:
            dex_data = json.load(dex_file)
            dexentry_key = f"cobblemon.species.{pokemon_name.lower()}.desc"
            dexentry = dex_data.get(dexentry_key, "No description available.")
        txt_file.write(f"|dexentry={dexentry}\n")

        # Finish writing PokeInfo section
        txt_file.write(f"|notice=Please visit the Bulbapedia page for [https://bulbapedia.bulbagarden.net/wiki/{pokemon_name}_(Pok%C3%A9mon) {pokemon_name}] if you would like more advanced information on this Pokemon, such as their evolutions and forms. This page is primarily for spawn and drop rate information until we get around to making a more advanced page.\n}}}}\n\n")

        # Write Drops section
        txt_file.write(f"{{{{PokeDrops|type1={pokemon_data.get('primaryType', '').capitalize()}}}}}\n")
        
        drops_data = pokemon_data.get("drops", {})
        amount = drops_data.get("amount", 1)
        entries = drops_data.get("entries", [])
        
        for entry in entries:
            item = format_item_name(entry.get("item", ""))
            quantity_range = entry.get("quantityRange", "1")
            percentage = entry.get("percentage", "100")
        
            txt_file.write(f"{{{{Drop|{item}|1|100}}}}\n")
        
        txt_file.write("|}\n|}\n")


        # Write Spawns section
        spawn_entries = extract_spawn_data(pokemon_name, spawn_folder)
        if spawn_entries:
            for spawn_entry in spawn_entries:
                conditions = spawn_entry.get("condition", {})
                anticonditions = spawn_entry.get("anticondition", {})
        
                def biome_cleanup(biome):
                    # Strip "cobblemon:is_" or "cobblemon:" prefixes
                    cleaned_biome = biome.replace("#cobblemon:is_", "").replace("#cobblemon:", "").replace("#the_bumblezone:", "").replace("#minecraft:is_", "").replace("#minecraft:", "")
                    # Replace underscores with spaces
                    cleaned_biome = cleaned_biome.replace("_", " ")
                    # Capitalize each word
                    cleaned_biome = cleaned_biome.title()
                    return f"[[{cleaned_biome}]]"
        
                # Write Biomes section
                biomes = conditions.get("biomes", [])
                biomes_list = ", ".join([biome_cleanup(biome) for biome in biomes])
                txt_file.write(f"{{{{SpawnInfo|type1={pokemon_data.get('primaryType', '').capitalize()}|biome={biomes_list}|\n")
        
                # Write AntiBiomes section
                antibiomes = anticonditions.get("biomes", [])
                antibiomes_list = ", ".join([biome_cleanup(biome) for biome in antibiomes])
                txt_file.write(f"|antibiome={antibiomes_list}\n")
        
                # Write Location section
                can_see_sky = conditions.get("canSeeSky", False)
                if can_see_sky:
                    txt_file.write("|location=Land\n")
                else:
                    txt_file.write("|location=Underground\n")
        
                # Write AntiLocation section
                anti_can_see_sky = anticonditions.get("canSeeSky", False)
                if anti_can_see_sky:
                    txt_file.write("|antilocation=Land\n")
                else:
                    txt_file.write("|antilocation=Underground\n")
        
                # Write Time section (assuming timeRange is present)
                time_range = conditions.get("timeRange", "Any")
                txt_file.write(f"|time={time_range.capitalize()}\n")
        
                # Write AntiTime section
                anti_time_range = anticonditions.get("timeRange", "Any")
                txt_file.write(f"|antitime={anti_time_range}\n")
        
                # Write Rarity section
                bucket = spawn_entry.get("bucket", "Unknown")
                txt_file.write(f"|rarity={bucket.capitalize()}\n")
        
                # Write Level Range section
                level_range = spawn_entry.get("level", "Unknown")
                txt_file.write(f"|levelrange={level_range}\n")
        
                # Finish the SpawnInfo section
                txt_file.write("}}\n")





        # Write Stats section
        base_stats = pokemon_data.get("baseStats", {})
        txt_file.write(f"{{{{Statbox|type1={pokemon_data.get('primaryType', '').capitalize()}|\n")
        txt_file.write(f"|hp={base_stats.get('hp', 'Unknown')}\n")
        txt_file.write(f"|atk={base_stats.get('attack', 'Unknown')}\n")
        txt_file.write(f"|def={base_stats.get('defence', 'Unknown')}\n")
        txt_file.write(f"|spatk={base_stats.get('special_attack', 'Unknown')}\n")
        txt_file.write(f"|spdef={base_stats.get('special_defence', 'Unknown')}\n")
        txt_file.write(f"|spe={base_stats.get('speed', 'Unknown')}}}")
        txt_file.write("}\n\n")

        # Write Moves section
        txt_file.write("{{MovesLayoutTop}}\n")
        # Level Moves
        txt_file.write(f"{{{{MovesAlign}}}}{{{{MovesLvlTop|{pokemon_data.get('primaryType', '').capitalize()}}}}}\n")
        moves = pokemon_data.get("moves", [])
        for move in moves:
            if move[0].isdigit():  # Check if the move starts with a number and assume they're level moves
                level, move_name = move.split(":")
                move_name = move_name.title()
                # Search for the move name in en_us.json and replace it if found with the proper spaced and capitalized version
                move_name_key = f"cobblemon.move.{move_name.lower()}"
                move_name_entry = dex_data.get(move_name_key)
                if move_name_entry:
                    move_name = move_name_entry
                move_name = move_name.replace(" ", "_")  # Replace spaces with underscores
                txt_file.write(f"{{{{movesLvl|{level}|{move_name}}}}}\n")
        txt_file.write("|}\n")

        # Write TM Moves section
        txt_file.write(f"{{{{MovesAlign}}}}{{{{MovesTmTop|{pokemon_data.get('primaryType', '').capitalize()}}}}}\n")
        for move in moves:
            if move.startswith("tm:"):
                move_name = move.split(":")[1]  # Strip the "tm:" prefix
                move_name = move_name.title()
                # Search for the move name in en_us.json and replace it if found with the proper spaced and capitalized version
                move_name_key = f"cobblemon.move.{move_name.lower()}"
                move_name_entry = dex_data.get(move_name_key)
                if move_name_entry:
                    move_name = move_name_entry
                move_name = move_name.replace(" ", "_")  # Replace spaces with underscores
                txt_file.write(f"{{{{movesTm|{move_name}}}}}\n")
        txt_file.write("|}\n")

        # Write Tutor Moves section
        txt_file.write(f"{{{{MovesAlign}}}}{{{{MovesTop|{pokemon_data.get('primaryType', '').capitalize()}}}}}\n")
        for move in moves:
            if move.startswith("tutor:"):
                move_name = move.split(":")[1]  # Strip the "tutor:" prefix
                move_name = move_name.title()
                # Search for the move name in en_us.json and replace it if found with the proper spaced and capitalized version
                move_name_key = f"cobblemon.move.{move_name.lower()}"
                move_name_entry = dex_data.get(move_name_key)
                if move_name_entry:
                    move_name = move_name_entry
                move_name = move_name.replace(" ", "_")  # Replace spaces with underscores
                txt_file.write(f"{{{{moves|{move_name}}}}}\n")
        txt_file.write("|}\n")

        # Write Breeding Moves section
        txt_file.write(f"{{{{MovesAlign}}}}{{{{MovesBTop|{pokemon_data.get('primaryType', '').capitalize()}}}}}\n")
        for move in moves:
            if move.startswith("egg:"):
                move_name = move.split(":")[1]  # Strip the "egg:" prefix
                move_name = move_name.title()
                # Search for the move name in en_us.json and replace it if found with the proper spaced and capitalized version
                move_name_key = f"cobblemon.move.{move_name.lower()}"
                move_name_entry = dex_data.get(move_name_key)
                if move_name_entry:
                    move_name = move_name_entry
                move_name = move_name.replace(" ", "_")  # Replace spaces with underscores
                txt_file.write(f"{{{{movesB|{move_name}}}}}\n")
        txt_file.write("|}\n|}\n")

        # Write NextPrev section again
        txt_file.write(f"{{{{NextPrev|dexprev={dexprev}|prev={prev_pokemon_name}|dexnext={dexnext}|next={next_pokemon_name}}}}}\n\n")


def get_ability(abilities, prefix, h=True):
    h_prefix = 'h:' if h else ''
    for ability in abilities:
        if ability.startswith(prefix):
            return ability[len(h_prefix):]
    return "Unknown"

def read_dex_file(dex_file_path):
    pokemon_map = {}
    with open(dex_file_path, "r") as dex_file:
        for line in dex_file:
            parts = line.strip().split()
            if len(parts) >= 2:
                pokemon_map[parts[0]] = ' '.join(parts[1:])
    return pokemon_map

def main():
    # Make sure to update these with the location of your folders and jsons
    pokemon_folder = r"C:\Users\changeme\Documents\WikiArchive\Wiki\Pokemon"
    spawn_folder = r"C:\Users\changeme\Documents\WikiArchive\Wiki\Spawns"
    output_folder = r"C:\Users\changeme\Documents\WikiArchive\Wiki\Pages"
    dex_file_path = r"C:\Users\changeme\Documents\WikiArchive\Wiki\Dex.txt"
    en_us_path = r"C:\Users\changeme\Documents\WikiArchive\Wiki\en_us.json"
    # Generated txt files of wiki pages will be placed into the Pages folder

    pokemon_map = read_dex_file(dex_file_path)

    for pokemon_file in os.listdir(pokemon_folder):
        if pokemon_file.endswith(".json"):
            pokemon_name = os.path.splitext(pokemon_file)[0]
            pokemon_path = os.path.join(pokemon_folder, pokemon_file)

            # Read the Pokemon JSON file to get the data
            with open(pokemon_path, "r") as json_file:
                pokemon_data = json.load(json_file)

            # Create the text file
            create_txt_file(pokemon_data, spawn_folder, output_folder, pokemon_map, en_us_path)

if __name__ == "__main__":
    main()
