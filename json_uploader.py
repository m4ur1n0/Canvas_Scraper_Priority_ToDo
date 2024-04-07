import json
import os
def overwrite_json(filename, dictionary):
    # try:
    #     with open(filename, "r") as file:
    #         existing_data = json.load(file)
        
    #     os.remove(filename)
    #     print("shoul")
    # except FileNotFoundError:
    #     existing_data = {}

    # # Update existing data with new dictionaries
    # for key, value in dictionary.items():
    #     existing_data[key] = value

    # OVERWRITE FILE COMPLETELY SAVE NOTHING FUCK THIS
    
    # Write the updated data back to the file
    with open(filename, "w") as file:
        json.dump(dictionary, file, indent=4)
