import os
import json

def transform_name(name):
    name = name.replace("generations_core:", "")
    name = name.replace("cobblemon:", "")
    name = name.replace("minecraft:", "")
    name = name.replace("_", " ").title()
    
    return name

def generate_txt_from_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
        
        items = data['pools'][0]['entries']
        
        output = ""
        for i, item in enumerate(items, start=1):
            name = item['name']
            if "tm" in name:
                tm_number = name.split("_")[-1]
                tm_type = get_tm_type(tm_number)
                output += "{{{{LootTm|{}|{}}}}}\n".format(tm_type, tm_number)
            else:
                name = transform_name(name)
                output += "{{{{Loot|{}}}}}\n".format(name)
            
            if i % 5 == 0 and i != len(items):
                output += "{{Span}}\n"
        
        txt_path = os.path.splitext(json_path)[0] + ".txt"
        with open(txt_path, 'w') as txt_file:
            txt_file.write(output)

def get_tm_type(tm_number):
    tm_file_path = os.path.join(os.path.dirname(__file__), 'tms.txt')
    with open(tm_file_path, 'r') as tm_file:
        for line in tm_file:
            parts = line.strip().split("=")
            if len(parts) == 2 and parts[0] == tm_number:
                return parts[1]
    return "Unknown"



def main():
    folder_path = '.'
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            json_path = os.path.join(folder_path, filename)
            generate_txt_from_json(json_path)

if __name__ == "__main__":
    main()
