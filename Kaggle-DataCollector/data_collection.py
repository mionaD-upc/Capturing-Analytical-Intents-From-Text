import json
import os
import requests
import time

def kaggle_search(searchQueries, headers=None, mode="qa"):
    base_folder=''
    if mode == "qa":
        url = "https://www.kaggle.com/api/i/discussions.DiscussionsService/GetTopicListByForumId"
        base_folder = "kaggle_search/QA"
        num_pages = int(input("Enter the number of pages to scrape (20 posts per page): "))
    elif mode == "competition":
        url = "https://www.kaggle.com/api/i/competitions.CompetitionService/ListCompetitions"
        base_folder = "kaggle_search/competitions"
        page_size = int(input("Enter the page size (num of results per page): "))
    else:
        raise ValueError("Invalid mode. Use 'qa' or 'competition'.")

    if headers is None:
        raise ValueError("Headers parameter is required.")

    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    for label in searchQueries:
        label_folder = os.path.join(base_folder, label)
        if not os.path.exists(label_folder):
            os.makedirs(label_folder)
        
        if mode == "qa":
            for page in range(1, num_pages + 1):
                payload = {
                    "category": "TOPIC_LIST_CATEGORY_ALL",
                    "group": "TOPIC_LIST_GROUP_ALL",
                    "customGroupingIds": [],
                    "author": "TOPIC_LIST_AUTHOR_UNSPECIFIED",
                    "filterCategoryIds": [],
                    "forumId": 2239,
                    "myActivity": "TOPIC_LIST_MY_ACTIVITY_UNSPECIFIED",
                    "page": page,
                    "recency": "TOPIC_LIST_RECENCY_UNSPECIFIED",
                    "searchQuery": label,
                    "sortBy": "TOPIC_LIST_SORT_BY_TOP"
                }

                response = requests.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    with open(os.path.join(label_folder, f"{label}_page_{page}.json"), "w") as file:
                        file.write(json.dumps(response.json(), indent=4))
                    print(f"Results for '{label}' from page {page} - saved successfully.")
                else:
                    print(f"Request failed for '{label}' on page {page} with status code:", response.status_code)
     
     
        elif mode == "competition":
            payload = {
                "selector": {
                    "competitionIds": [],
                    "listOption": "LIST_OPTION_DEFAULT",
                    "sortOption": "SORT_OPTION_NUM_TEAMS",
                    "hostSegmentIdFilter": 0,
                    "searchQuery": label,
                    "prestigeFilter": "PRESTIGE_FILTER_UNSPECIFIED",
                    "participationFilter": "PARTICIPATION_FILTER_UNSPECIFIED",
                    "tagIds": [],
                    "excludeTagIds": [],
                    "requireSimulations": False,
                    "requireKernels": False
                },
                "pageToken": "",
                "pageSize": page_size,
                "readMask": "competitions,competitionUsers,totalResults,thumbnailImageUrls,headerImageUrls"
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                with open(os.path.join(label_folder, f"{label}.json"), "w") as file:
                    file.write(json.dumps(response.json(), indent=4))
                print(f"{page_size} competitions for '{label}' saved successfully.")
            else:
                print(f"Request failed for '{label}' with status code:", response.status_code)

    return base_folder


def extract_post_urls(folder_path):
    post_urls = []
    mode = folder_path.split('/')[-2]
    if(mode=='QA'):
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    for topic in data['topics']:
                        topic_url = "https://www.kaggle.com" + topic['topicUrl']
                        post_urls.append((filename, topic_url))
    elif(mode=='competitions'):
            for filename in os.listdir(folder_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r') as file:
                        data = json.load(file)
                        for competition in data['competitions']:
                            competition_url = "https://www.kaggle.com" + "/competitions/" +  str(competition['id'])
                            post_urls.append((filename, competition_url))    

    print("Number of urls : " + str(len(post_urls))) 
    return post_urls


def get_post(filename, post_url, headers=None, mode="qa"):
    base_folder = ''
    if mode == 'qa':
        base_folder = "kaggle_content/QA"
        code = post_url.split('/')[-1]
        payload = {"forumTopicId": code, "includeComments": True}
        url = "https://www.kaggle.com/api/i/discussions.DiscussionsService/GetForumTopicById"
        folder = filename.replace(".json", "")
        file_name = os.path.join(base_folder, folder, code + ".json")
       

    elif mode=='competition':
        base_folder = "kaggle_content/competitions"
        code = post_url.split('/')[-1]
        payload = {"competitionId":code}
        url = 'https://www.kaggle.com/api/i/competitions.PageService/ListPages'
        folder = filename.replace(".json", "")
        file_name = os.path.join(base_folder, folder.split('/')[-1], code + ".json")
       

    response = requests.post(url, json=payload, headers=headers)
        
    if response.status_code == 200:
            
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
            
        # Save response content to a JSON file
        with open(file_name, "w") as file:
            file.write(json.dumps(response.json(), indent=4))
            
        print(f"Response saved successfully as '{file_name}'.")
    else:
        print(f"Request failed for '{post_url}' with status code:", response.status_code)


def close_json(file_path, existing_data):
    with open(file_path, 'w') as file:
        file.write('[\n')
        for i, entry in enumerate(existing_data):
            if i != 0:
                file.write(',\n')
            file.write(json.dumps(entry,indent=4))
        file.write('\n]')


def get_codeList_per_mode_and_label(mode, url, label):
    file_path = 'retrieved-codes.json'

    code = url.split('/')[-1]
    if code not in codes_count:
        codes_count[code] = 1
    else:
        codes_count[code] += 1

    data = {
        "mode": mode,
        "label": label,
        "codes": {
            "list": list(codes_count.keys()),
            "count": len(codes_count)
        }
    }
    
    existing_data = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            existing_data = json.load(file)

    overwritten = False

    for i, entry in enumerate(existing_data):
        if entry.get("mode") == mode and entry.get("label") == label:
            existing_data[i] = data
            overwritten = True
            break

    if not overwritten:
        existing_data.append(data)

    close_json(file_path=file_path, existing_data=existing_data)
         

# Example :

if __name__ == "__main__":
    
## searchQuery candidates 
    searchQueries = ["clustering"] ## Define here

    headers = {
            "Content-Type": "application/json",
            "Cookie": "<COOKIE>",
            "X-Xsrf-Token": "<TOKEN>"
    }

    mode = input("Enter mode ('qa' for QA, 'competition' for Competitions): ")
    result_path = kaggle_search(searchQueries, headers=headers, mode=mode)

    for label in searchQueries:
        codes_count = {}
        search_urls = extract_post_urls(result_path + "/" + label)
        for filename, url in search_urls:
            get_post(label + "/" + filename, url, headers=headers, mode=mode)
            time.sleep(1)
            get_codeList_per_mode_and_label(mode=mode,url=url, label=label)