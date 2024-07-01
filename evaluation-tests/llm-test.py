from openai import OpenAI
from llamaapi import LlamaAPI
import os
from datetime import datetime
from sklearn.metrics import confusion_matrix, recall_score, classification_report, accuracy_score
import numpy as np
import os
import re
import sys
from dotenv import load_dotenv


ALLOWED_PROVIDERS = ["gpt", "mistral", "meta"]

def get_predictionLLama_Mistral(llama, content, labels, model, forced = None):
    api_request_json = {
        "model": model,
        "messages": [
            {"role": "user", "content": content},
        ]
    }
    response = llama.run(api_request_json)
    response_data = response.json()
    prediction = None
    for choice in response_data['choices']:
        if choice['message']['role'] == 'assistant':
            prediction = choice['message']['content']
            break
    if forced:
        match = re.search(r'\{"answer": "(.*?)"\}', prediction)
        if match:
            label_predicted = match.group(1)
            if label_predicted in labels:
                return label_predicted
            else:
                for label in labels:
                    pattern = re.escape(label)
                    if re.search(pattern, label_predicted, re.IGNORECASE):
                        return label
        
        # print(prediction)
        return "unknown"
    else:
        for label in labels:
                pattern = re.escape(label)
                if re.search(pattern, prediction, re.IGNORECASE):
                    return label
        return "unknown"  # Return "unknown" if no label is found

def get_predictionGPT(content, labels, model, forced = None):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}]
    )
    prediction = completion.choices[0].message.content.lower()

    if forced:
        # print(prediction)
        match = re.search(r'\{"answer": "(.*?)"\}', prediction)
        if match:
            label_predicted = match.group(1)
            if label_predicted in labels:
                return label_predicted
            else:
                for label in labels:
                    pattern = re.escape(label)
                    if re.search(pattern, label_predicted, re.IGNORECASE):
                        return label
        return "unknown"
    else:
        for label in labels:
                pattern = re.escape(label)
                if re.search(pattern, prediction, re.IGNORECASE):
                    return label
        return "unknown"  # Return "unknown" if no label is found


def main(llm_provider, model_name, file_path):

    if llm_provider not in ALLOWED_PROVIDERS:
        print(f"Invalid LLM provider. Allowed values are: {', '.join(ALLOWED_PROVIDERS)}")
        return
    if not os.path.exists(file_path):
        print("File path does not exist.")
        return
    if not os.path.isdir(file_path):
        print("Specified path is not a directory.")
        return

    load_dotenv() 
    if llm_provider == 'mistral' or llm_provider=='meta':
        llama_key = os.getenv("LlamaAPI_KEY")
        llama = LlamaAPI(llama_key)

    labels = os.listdir(file_path)
    labels = [label for label in labels if os.path.isdir(os.path.join(file_path, label))]
    labels_content = [label.replace('"', '`') for label in labels]
    terminal_width = os.get_terminal_size().columns

    main_folder = file_path
    type = main_folder.split('/')[-1]

    labels_andUnknown = labels + ["unknown"]
    content_forced = ''

    predictions = []
    ground_truth_labels = []
    unknown_count = 0  # Counter for "unknown" returns

    start_time = datetime.now()  # Start timing here
    for label_folder in os.listdir(main_folder):
        print('-'*terminal_width)
        print("Obtaining predictions for class: "  + label_folder)        
        label_path = os.path.join(main_folder, label_folder)
        if os.path.isdir(label_path) and label_folder in labels:
            # Load each text file and obtain prediction
            for file_name in os.listdir(label_path):
                file_path = os.path.join(label_path, file_name)
                if file_name.endswith(".txt") and os.path.isfile(file_path):
                    with open(file_path, "r") as file:
                        text = file.read()
                        content = f"""Classes: {labels_content}\nText: {text}\n\nClassify the text into one of the above classes."""
                        if(llm_provider =='gpt'):
                            prediction = get_predictionGPT (content, labels, model=model_name,  forced = False)
                            if prediction == "unknown":
                                content_forced = f"""Text: {text}\n\nClassify the text into only one of the following classes: {labels_content}. Your answer must be in JSON format: {{"answer": "class"}} and the class must be present in {labels_content}"""
                                prediction = get_predictionGPT (content_forced, labels, model=model_name, forced=True)
                                if prediction =='unknown':  
                                    unknown_count += 1 
                        elif(llm_provider=='meta' or llm_provider =='mistral'):
                            prediction = get_predictionLLama_Mistral (llama, content, labels, model=model_name, forced = False)
                            if prediction == "unknown":
                                content_forced = f"""Text: {text}\n\nClassify the text into only one of the following classes: {labels_content}. Your answer must be in JSON format: {{"answer": "class"}} and the class must be present in {labels_content}"""
                                prediction = get_predictionLLama_Mistral (llama, content_forced, labels, model=model_name, forced = True)
                                if prediction =='unknown':  
                                    unknown_count += 1
                        # print('-'*terminal_width)
                        # print(content)
                        # print('-'*terminal_width)
                        ground_truth_labels.append(label_folder)
                        predictions.append(prediction)
                        # print("Prediction: " +  prediction)
    stop_time = datetime.now()  # Stop timing here
    elapsed_time = stop_time - start_time  # Calculate elapsed time
    print("Time taken to classify validation data:", elapsed_time)
    print('-'*terminal_width)
    print("Unknown count:", unknown_count)
    # print(predictions)
    # print(ground_truth_labels)
# Compute metrics
    accuracy = accuracy_score(ground_truth_labels, predictions)

    print("Accuracy: " + str(accuracy))
    
    recall = recall_score(ground_truth_labels, predictions, average="micro")

    print("\nRecall: " + str(recall))

    print("\nConfusion matrix: \n")
    if unknown_count!=0:
        print(confusion_matrix(y_true=ground_truth_labels, y_pred=predictions, labels=labels_andUnknown))
    else:
      print(confusion_matrix(y_true=ground_truth_labels, y_pred=predictions, labels=labels))

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    dir = f"evaluation-results/{llm_provider}/{model_name}/" + type
    os.makedirs(dir, exist_ok=True)  # Ensure directory creation or skip if it already exists
        
    str_1 = "# Evaluation of {} \n".format(timestamp)
    str_2 = "## Classification report: \n"
    class_report = classification_report(y_true=ground_truth_labels, y_pred=predictions)

    file_name = os.path.join(dir, model_name + '-' + timestamp + "_" + "eval.txt")

    file = open(file_name, "w")
    file.write(str_1 + str_2 + class_report)
    file.close()

if __name__ == '__main__':
    if len(sys.argv) != 7 or sys.argv[1] != '--provider' or sys.argv[3] != '--model' or sys.argv[5] != '--path':
        print("Usage: python script.py --provider <llm_provider> --model <model_name> --path <file_path>")
        sys.exit(1)
    llm_provider = sys.argv[2]
    model_name = sys.argv[4]
    file_path = sys.argv[6]
    main(llm_provider, model_name, file_path)