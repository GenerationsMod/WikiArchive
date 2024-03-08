import csv
import json
import os


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


def generate_crafting_recipe(item_id):
    recipe_folder = "recipes"
    recipe_file = os.path.join(recipe_folder, f"{item_id}.json")

    if not os.path.exists(recipe_file):
        print(f"Recipe file not found for '{item_id}'. Skipping...")
        return ""

    with open(recipe_file, "r", encoding="utf-8") as file:
        recipe_data = json.load(file)
        recipe_type = recipe_data.get("type", "")
        if recipe_type == "crafting shaped":
            pattern = recipe_data.get("pattern", [])
            key = recipe_data.get("key", {})
            crafted_item = recipe_data.get("result", {}).get("item", "")
            crafted_item = crafted_item.title()  # Capitalize each word in the crafted item name
            recipe_grid = "|recipe=\n{{Grid/Crafting Table\n"
            for row_idx, row in enumerate(pattern):
                row_data = ""
                for col_idx, char in enumerate(row):
                    grid_pos = f"{chr(65 + col_idx)}{row_idx + 1}"  # Convert 0-based indices to A1, B2, etc.
                    if char in key:
                        item_name = key[char].get("item", "").title()  # Capitalize each word in the item name
                        row_data += f"|{grid_pos}={item_name}"
                    else:
                        row_data += f"|{grid_pos}="
                recipe_grid += row_data + "\n"
            recipe_grid += f"|Output={crafted_item}|shapeless=n}}}}"
            return recipe_grid
        elif recipe_type == "crafting shapeless":
            ingredients = recipe_data.get("ingredients", [])
            crafted_item = recipe_data.get("result", {}).get("item", "")
            crafted_item = crafted_item.title()  # Capitalize each word in the crafted item name
            recipe_grid = "|recipe=\n{{Grid/Crafting Table\n"
            grid_pos = ["A1", "B1", "C1", "A2", "B2", "C2", "A3", "B3", "C3"]
            for idx, ingredient in enumerate(ingredients):
                if idx >= len(grid_pos):
                    print(f"Too many ingredients for '{item_id}'. Skipping...")
                    return ""
                item_name = ingredient.get("item", "").title()  # Capitalize each word in the item name
                recipe_grid += f"|{grid_pos[idx]}={item_name}"
            # Fill the rest of the grid with empty slots
            for idx in range(len(ingredients), len(grid_pos)):
                recipe_grid += f"|{grid_pos[idx]}="
            recipe_grid += f"|Output={crafted_item}|shapeless=y}}}}"
            return recipe_grid
        else:
            print(f"Unknown recipe type for '{item_id}'. Skipping...")
            return ""







def generate_item_text(item_name, item_id, description, loot_matches, crafting_recipe):
    drop_loot_info = "{{{{DropLoot|{}}}}}".format('|'.join(filename.replace('.json', '=y') for filename in loot_matches)) if loot_matches else "None"
    return read_template().replace("Item Name", item_name).replace("item_name", item_id.lower().replace(" ", "_")).replace("Description", description).replace("drop1=drop_loot_info pokemon_drops", f"drop1={drop_loot_info}").replace("recipe_here", crafting_recipe)


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
            crafting_recipe = generate_crafting_recipe(item_id)
            item_text = generate_item_text(item_name, item_id, description, loot_matches, crafting_recipe)
            with open(os.path.join(output_folder, f"{item_name}.txt"), "w", encoding="utf-8") as output_file:
                output_file.write(item_text)


if __name__ == "__main__":
    main()
