import requests
from bs4 import BeautifulSoup
import os
import re
import time
import json

def extract_links(searchQueries, headers, payload):
    all_links = []
    all_files = []

    for query in searchQueries:
        if len(query) == 1:
            tags = query
            tags_string = f"%5b{tags[0]}%5d"
            s=''
        else:
            tags = query[:-1]  # Extract tags from the query
            logical_operator = query[-1].lower()  # Extract logical operator (AND/OR)
            tags_string = f"%20{logical_operator}%20".join([f"%5b{tag}%5d" for tag in tags])
            s = f"-{logical_operator}-"

        
        url = f"https://stats.stackexchange.com/questions/tagged/{tags_string}?sort=MostVotes&page=3"
        response = requests.get(url, headers=headers, params=payload)
        
        print("\nHttp request made to url:")
        print(url + "\n")

        if response.status_code == 200:

            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            h3_links = soup.find_all('h3')  # Assuming all links are within <h3> tags
            links = [h3.a['href'] for h3 in h3_links if h3.a and h3.a['href'].startswith('/questions/')]
            all_links.extend(links)
            
            filename = s.join(tags) + '.txt'
            directory = 'links'
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, filename)
            
            with open(file_path, 'a') as file:
                for link in links:
                    file.write("https://stats.stackexchange.com" + link + '\n')

            print(str(len(links)) + f" links have been extracted and stored in 'links/{filename}'.\n")
            all_files.append(filename)
        
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")

    return all_links, all_files

def get_responses_from_links(file_path, headers):
    pattern = r'/(\d+)/'
    payload = {
        "r": "SearchResults",
        "pagesize": "50"  # Adjusted to get 50 results
    }
    
    folder_name = "content/" + os.path.splitext(os.path.basename(file_path))[0]
    label = os.path.splitext(os.path.basename(file_path))[0]
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    retrived_urls = {}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            match = re.search(pattern, line.strip())
            if match:
                code = match.group(1)
                url = line.strip() 
                response = requests.get(url, headers=headers, params=payload)
                
                if response.status_code == 200:
                    file_name = f"{code}.html"
                    file_path = os.path.join(folder_name, file_name)
                    with open(file_path, 'w') as response_file:
                        response_file.write(response.text)
                        print(f"Response saved as {file_path}")
                        
                    if label in retrived_urls:
                        if 'codes' in retrived_urls[label]:
                            if code not in retrived_urls[label]['codes']:
                                retrived_urls[label]['codes'].append(code)
                        else:
                            retrived_urls[label]['codes'] = [code]
                    else:
                        retrived_urls[label] = {'codes': [code]}
                        
                else:
                    print(f"Failed to fetch data from {url}. Status code: {response.status_code}\n")

            time.sleep(1)
    
    for folder, data in retrived_urls.items():
        data['count'] = len(data['codes'])
    
    if retrived_urls:
        json_file_path = "retrieved-urls.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                existing_data = json.load(json_file)
                existing_data.update(retrived_urls)
        else:
            existing_data = retrived_urls
        
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
    
    

# Example usage:

searchQueries = [
    ["association-rules"],
]



headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Cookie": "<COOKIE>"
}

payload = {
    "sort": "MostVotes",
    "pagesize": "50",
}

links, files = extract_links(searchQueries, headers, payload)

for file in files:
    get_responses_from_links('links/' + file, headers=headers)
    time.sleep(10)
    print("\n")

