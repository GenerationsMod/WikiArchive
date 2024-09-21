import os
import json

#This script scans a cobblemon species folder where this script is ran from (ie put this in the species folder) and deletes spawns if they are implemented by cobblemon and are not legendary, mythical, or paradox

# Deletes the spawn files in this location
TARGET_PATH = r"C:\Users\Nobody\Documents\GitHub\Generations-Core\common\src\main\resources\data\cobblemon\spawn_pool_world"

def find_json_files(directory):
    """
    Recursively find all .json files in a directory.
    """
    json_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files

def check_json_for_implemented_and_labels(file_path):
    """
    Check if a JSON file contains "implemented": true and if it does not contain
    "mythical", "legendary", or "paradox" in the "labels".
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Check if "implemented" is true
            if data.get("implemented") != True:
                return False
            
            # Check if "mythical", "legendary", or "paradox" are in "labels"
            labels = data.get("labels", [])
            if any(label in labels for label in ["mythical", "legendary", "paradox"]):
                print(f"Skipping {file_path} due to 'mythical', 'legendary', or 'paradox' in labels.")
                return False
            
            return True
    except json.JSONDecodeError:
        print(f"Error reading {file_path} - invalid JSON")
        return False

def delete_matching_files(implemented_filename, target_path):
    """
    Search for a file in the target path that ends with the same filename as the implemented one
    and delete it if found.
    """
    for root, _, files in os.walk(target_path):
        for file in files:
            if file.endswith(implemented_filename):
                full_path = os.path.join(root, file)
                try:
                    os.remove(full_path)
                    print(f"Deleted: {full_path}")
                except OSError as e:
                    print(f"Error deleting {full_path}: {e}")

def main():
    current_directory = os.getcwd()

    json_files = find_json_files(current_directory)

    for json_file in json_files:
        if check_json_for_implemented_and_labels(json_file):
            filename = os.path.basename(json_file)
            print(f"'implemented: true' found in {filename}, no mythical, legendary, or paradox labels.")

            delete_matching_files(filename, TARGET_PATH)

if __name__ == "__main__":
    main()
