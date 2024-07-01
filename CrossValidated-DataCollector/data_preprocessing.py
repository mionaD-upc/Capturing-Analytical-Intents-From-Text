from bs4 import BeautifulSoup
from langdetect import detect
import emoji
import re
import os
import json


def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False 

def remove_emoji(string):
    return emoji.replace_emoji(string, replace='')

def preprocess_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    
    div = soup.find('div', class_='s-prose js-post-body')
    if div:
        paragraphs = []

        for p in div.find_all('p'):
            for img in p.find_all('img'):
                img.extract()
            for a in p.find_all('a'):
                a.extract()
            for code in p.find_all('code'):
                code.extract()

            p_text = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', p.get_text().strip(), flags=re.DOTALL)
            
            p_text = re.sub(r'\$\$.*?\$\$', '', p_text, flags=re.DOTALL)
            
            p_text = re.sub(r'\$.*?\$', '', p_text)
            
            p_text = re.sub(r'\\[a-zA-Z]+(?:\{.*?\})*', '', p_text)
            
            p_text = re.sub(r'&[a-zA-Z]+;', '', p_text)
            
            paragraphs.append(remove_emoji(p_text.strip()))

        extracted_text = '\n'.join(paragraphs)

        if is_english(extracted_text):
            return extracted_text
        else:
            return None
    else:
        return None
    
def getCleanTxt_Content(content_path):
    
    save_dir = "crossValidated-validation_data"
    disregarded_urls = {}


    for folder_name in os.listdir(content_path):
                print(folder_name)
                count = 0
                folder_path = os.path.join(content_path, folder_name)
                disregarded_urls[folder_name] = {
                    "codes": [],
                    "count": 0
                }
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                   
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                    preprocessed_content = preprocess_text(text=text)  
                        
                    if preprocessed_content is not None:
                        save_file_path = os.path.join(save_dir, folder_name)
                        file_name = file_name.replace(".html", "")

                        file_path = os.path.join(save_file_path, file_name + ".txt")

                        os.makedirs(save_file_path, exist_ok=True)
                        with open(file_path, 'w') as save_file:
                            save_file.write(preprocessed_content)
                        count+=1
                    else: 
                        print(f"\nFile path: {file_path} - Text is not in English / Content not available and will not be saved inside {save_file_path}")   
                        disregarded_urls[folder_name]["codes"].append(file_name)
                        disregarded_urls[folder_name]["count"] += 1                 
                    
                print(f"\nSuccessfully preprocessed {count} files from {folder_path} and stored inside {save_file_path}\n") 
                print("-----------------------------------------------------------------------------------------------------")
        
    if any(value["count"] > 0 for value in disregarded_urls.values()):
     with open('disregarded-urls.json', 'w') as f:
        json.dump(disregarded_urls, f, indent=4)

   
content_path = "content"
getCleanTxt_Content(content_path=content_path)
