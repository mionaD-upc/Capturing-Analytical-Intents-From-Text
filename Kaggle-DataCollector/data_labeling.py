import os
import json

def check_labels(folder_path, mode):
    width = os.get_terminal_size().columns 

    if not os.path.exists(folder_path):
        print(f"The path '{folder_path}' does not exist.")
        return

    incorrect_files = []

    json_file_path = 'incorrectly-labeled-files.json'
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            incorrect_files = json.load(json_file)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                
                print(f"Label: {os.path.basename(root)}")
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        print(f"\nFile Content: \n{content}")
                        print('-' * width)

                except Exception as e:
                    print(f"Error reading file {file_path}: {e}\n")
                    continue
                
                user_input = input("Is the label accurate for the content? (yes/no): ").lower()
                print('#' * width)
                print("\n")
                
                if user_input != 'yes':
                    folder_name = os.path.basename(root)
                    existing_entry = next((item for item in incorrect_files if item["label"] == folder_name and item["mode"]==mode), None)
                    
                    if not existing_entry:
                        existing_entry = {
                            "mode": mode,
                            "label": folder_name,
                            "file_names": [],
                            "status": "not suited"
                        }
                        incorrect_files.append(existing_entry)

                    if file not in existing_entry["file_names"]:
                        existing_entry["file_names"].append(file)

                    try:
                        os.remove(file_path)
                        print(f"Removed {file} from {folder_name}\n")
                    except Exception as e:
                        print(f"Error removing file {file_path}: {e}\n")

    if incorrect_files:
        try:
            with open(json_file_path, 'w') as json_file:
                json.dump(incorrect_files, json_file, indent=4)
            print(f"List of incorrectly labeled files has been saved to '{json_file_path}'.")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

if __name__ == "__main__":
    
    print("\nThe primary objective of this tool is to validate the correct assignment of files to their respective labels.\nA prerequisite for its operation is the existence of a folder containing data, along with a specified mode that facilitates navigation to a subfolder.\nWithin this subfolder, each subsequent subdirectory is designated by a unique label.\n")
    folder_path = input("Enter the path to the main folder: ")
    mode = input("Enter mode ('qa' for QA, 'competition' for Competitions): ")
    if mode =='qa':
        folder_path = folder_path + "/QA"
    elif mode=='competition':
     folder_path = folder_path + "/competitions"
    else:
        raise ValueError("Invalid mode. Use 'qa' or 'competition'.")
    print("\n")
    check_labels(folder_path, mode)
