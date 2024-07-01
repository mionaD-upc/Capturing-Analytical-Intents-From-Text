import json
import os
from bs4 import BeautifulSoup
import emoji
import markdown
import re
from langdetect import detect

def getDisregarded_CodeList(code, label, mode):
    new_data = {
        "mode": mode,
        "label": label,
        "codes": {
            "list": [],
            "count": 0
        }
    }
    if os.path.exists('disregarded-codes.json'):
        with open('disregarded-codes.json', 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    found_existing_entry = False
    for entry in existing_data:
        if entry['label'] == label and entry['mode'] == mode:
            codes_list = entry['codes']['list']
            if code not in codes_list:
                codes_list.append(code)
            found_existing_entry = True
            break
    
    if not found_existing_entry:
        new_data['codes']['list'].append(code)
        existing_data.append(new_data)
    
    for entry in existing_data:
        entry['codes']['count'] = len(entry['codes']['list'])
    
    with open('disregarded-codes.json', 'w') as f:
        json.dump(existing_data, f, indent=2)


def preprocess_md(md_text):
    html = markdown.markdown(md_text)
    return preprocess_text(html)
    
def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False 
    

def remove_emoji(string):
    return emoji.replace_emoji(string, replace='')

def preprocess_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    
    paragraphs = []
    for p in soup.find_all('p'):
        for img in p.find_all('img'):
            img.extract()
        for a in p.find_all('a'):
            a.extract()
        for code in p.find_all('code'):
            code.extract()

        paragraphs.append(remove_emoji(p.get_text().strip()))

    extracted_text = '\n'.join(paragraphs)
    extracted_text= re.sub(r'#\w+', '', extracted_text)


    if is_english(extracted_text):
        return extracted_text
    else:
        return None

def getCleanTxt_kaggleContent(content_path):
    if "competitions" in content_path:
        for folder_name in os.listdir(content_path):
            count = 0
            folder_path = os.path.join(content_path, folder_name)
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                # print(file_path)
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                save_dir = "kaggle-validation_data/competitions"
                description_content = None
                for page in data["pages"]:
                    if page.get("name") == "Description" and page.get("content") is not None:
                        description_content = page["content"]
                        break  # Break out of the loop after finding the Description page with content
                
                file_name = os.path.splitext(file_name)[0]

                if description_content is not None:
                    preprocessed_content = preprocess_md(description_content)
                    save_file_path = os.path.join(save_dir, folder_name)
                    label = save_file_path.split('/')[-1]
                    mode = save_file_path.split('/')[-2].lower()[:-1]

                    if preprocessed_content is not None:
                        os.makedirs(save_file_path, exist_ok=True)
                        # print(save_file_path)

                        file_path = os.path.join(save_file_path, file_name + ".txt")   
                        
                        with open(file_path, 'w') as save_file:
                            save_file.write(preprocessed_content)
                            count+=1
                    else: 
                        print(f"\nFile path: {file_path} - Invalid content - not saved inside {save_file_path}\n")
                        getDisregarded_CodeList(file_name, label, mode)
                       
                else:
                    print(f"Description not available or has no content in the file: {file_path}\n")
                    getDisregarded_CodeList(file_name, label, mode)

        
            print(f"Successfully preprocessed {count} files from {folder_path} and stored inside {save_file_path}\n") 
            print('-' * width)
            print("\n")
   
    elif "QA" in content_path:

        for folder_name in os.listdir(content_path):
            count = 0

            # print(folder_name)
            folder_path = os.path.join(content_path, folder_name)
            for sub_folder in os.listdir(folder_path):
                sub_folder_path = os.path.join(folder_path, sub_folder)
                for file_name in os.listdir(sub_folder_path):
                    file_path = os.path.join(sub_folder_path, file_name)
                    # print(file_path)
                    with open(file_path, 'r') as json_file:
                            data = json.load(json_file)
                    save_dir = "kaggle-validation_data/QA"

                    content = data.get('forumTopic', {}).get('firstMessage', {}).get('content')
                    if content is not None:
                        preprocessed_content = preprocess_text(content)
                        file_name = os.path.splitext(file_name)[0]
                        save_file_path = os.path.join(save_dir, folder_name)
                        label = save_file_path.split('/')[-1]
                        mode = save_file_path.split('/')[-2].lower()


                        if preprocessed_content is not None:
                            os.makedirs(save_file_path, exist_ok=True)
                            file_path = os.path.join(save_file_path, file_name + ".txt")
                        
                            
                            with open(file_path, 'w') as save_file:
                                save_file.write(preprocessed_content)
                                count+=1

                        else: 
                            print(f"File path: {file_path} - Invalid content - not saved inside {save_file_path}\n")
                            getDisregarded_CodeList(file_name, label, mode)
                    else:
                        print(f"Content not available in the file: {file_path}\n")
                        file_name = os.path.splitext(file_name)[0]

                        getDisregarded_CodeList(file_name, label, mode)
                        
            print(f"Successfully preprocessed {count} files from {folder_path} and stored inside {save_file_path}\n")
            print('-' * width)
    
    else:
        print("Error: Invalid file path. It must contain QA or competitions (e.g. kaggle_content/QA)")



## Example usage:
if __name__ == "__main__":
    
    width = os.get_terminal_size().columns 

    print("\nPREPROCESS QA/Competition files from kaggle_content:\n")
    mode = input("Enter mode ('qa' for QA, 'competition' for Competitions): ")
    print('-' * width)

    if mode =='qa':
        kaggle_content_path = "kaggle_content/QA"
    elif mode=='competition':
        kaggle_content_path = "kaggle_content/competitions"
    else:
        raise ValueError("Invalid mode. Use 'qa' or 'competition'.")

    getCleanTxt_kaggleContent(content_path=kaggle_content_path)
