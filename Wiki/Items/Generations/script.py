import csv
import json
import os
import re

#For me: php maintenance/importTextFiles.php --overwrite --use-timestamp ImportPages/*.txt
def read_template():
    with open("template.txt", "r", encoding="utf-8") as file:
        return file.read()


def find_item_description(item_name, csv_file):
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0].lower() == item_name.lower():
                return row[1]
    return ""


def find_loot_matches(item_id):
    loot_matches = []
    for filename in os.listdir("loots"):
        if filename.endswith(".json"):
            with open(os.path.join("loots", filename), "r", encoding="utf-8") as file:
                data = json.load(file)
                for pool in data.get("pools", []):
                    for entry in pool.get("entries", []):
                        name = entry.get("name", "")
                        if item_id.lower() == name:
                            loot_matches.append(filename)
                            print(f"Found match in {filename}: {name}")
                            break  # No need to continue checking entries
    return loot_matches







def find_pokemon_drops(item_id):
    pokemon_drops = []
    for filename in os.listdir("Pokemon"):
        if filename.endswith(".json"):
            with open(os.path.join("Pokemon", filename), "r", encoding="utf-8") as file:
                data = json.load(file)
                for drop in data.get("drops", {}).get("entries", []):
                    if drop.get("item", "").lower() == item_id.lower():
                        pokemon_name = data.get("name", "")
                        if pokemon_name:
                            pokemon_drops.append("[[{}]]".format(pokemon_name))
                            print(f"Found match in {filename}: {pokemon_name}")
                        break  # No need to continue checking drops
    return pokemon_drops


def generate_item_text(item_name, item_id, description, loot_matches):
    drop_loot_info = "{{{{DropLoot|{}}}}}".format('|'.join(filename.replace('.json', '=y') for filename in loot_matches)) if loot_matches else ""
    pokemon_drops = find_pokemon_drops(item_id)
    drop_info = f"{drop_loot_info} {', '.join(pokemon_drops)}" if loot_matches or pokemon_drops else ""
    return read_template().replace("Item Name", item_name).replace("item_name", item_id.lower().replace(" ", "_")).replace("Description", description).replace("drop1=drop_loot_info pokemon_drops", f"drop1={drop_info}")


def main():
    template = read_template()
    en_us_path = "en_us.json"
    items_csv_path = "items.csv"
    output_folder = "Generated"
    os.makedirs(output_folder, exist_ok=True)

    with open(en_us_path, "r", encoding="utf-8") as file:
        en_us_data = json.load(file)

    with open(items_csv_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            item_name = row[0]
            item_id = row[0]
            if item_name not in en_us_data.values():
                print(f"Item '{item_name}' not found in en_us.json. Skipping...")
                continue
            description = find_item_description(item_name, items_csv_path)
            loot_matches = find_loot_matches(item_id)
            item_text = generate_item_text(item_name, item_id, description, loot_matches)
            with open(os.path.join(output_folder, f"{item_name}.txt"), "w", encoding="utf-8") as output_file:
                output_file.write(item_text)


if __name__ == "__main__":
    main()
