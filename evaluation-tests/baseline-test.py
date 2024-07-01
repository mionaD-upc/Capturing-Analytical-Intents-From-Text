from datetime import datetime
import os
from helper_functions import *
from rs_helper.core import *
from rs_helper.helper import *
from typing import *
from rs_helper import RecommendationFacade

# Requires : https://github.com/rsmttud/Recommender-System/tree/master?tab=readme-ov-file


def get_predictionMD(pipeline_method: str, file_name: str) -> Prediction:
    """
   Modified get_prediction to return Prediction instead of Dict
    """
    path_long_desc = os.path.join(file_name)
    facade = RecommendationFacade(path_to_files=path_long_desc)

    result = facade.recommend()
    result.scale_log()
    result.round_values()
 
    return result

if __name__ == '__main__':

    terminal_width = os.get_terminal_size().columns

    main_folder = 'data/validation-data/baseline-class-coverage/eval_data'
    labels = ["clustering", "pattern_mining", "prediction"]

    main_folder_path = os.path.join(os.getcwd(), main_folder)

    predictions = []
    ground_truth_labels = []
    start_time = datetime.now()  # Start timing here
    for label_folder in os.listdir(main_folder_path):
        print('-'*terminal_width)
        print("Obtaining predictions for class: "  + label_folder)
        label_path = os.path.join(main_folder_path, label_folder)
        if os.path.isdir(label_path) and label_folder in labels:
            # Load each text file and obtain prediction
            for file_name in os.listdir(label_path):
                file_path = os.path.join(label_path, file_name)
                if file_name.endswith(".txt") and os.path.isfile(file_path):
                    prediction = get_predictionMD("", file_path)    
                    predictions.append(prediction)
                    ground_truth_labels.append(label_folder)
            # print(predictions)
            # print("\n")
            # print(ground_truth_labels)
    stop_time = datetime.now()  # Stop timing here
    elapsed_time = stop_time - start_time  # Calculate elapsed time
    print("Time taken to classify validation data:", elapsed_time)

    print('-'*terminal_width)
    # print(predictions)
    # print(ground_truth_labels)

    # Instantiate SystemEvaluation
    evaluation = SystemEvaluation(predictions, ground_truth_labels)

    # Retrieve evaluation metrics
    accuracy = evaluation.calculate_accuracy_score()
    recall = evaluation.calculate_recall()
    conf_matrix = evaluation.get_confusion_matrix()
    print("Confusion Matrix:")
    print(conf_matrix)

    save_dir = "plots"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    save_path = os.path.join(save_dir, f"confusion_matrix_{timestamp}.png")

    # Plot the confusion matrix
    confusion_matrix_plot(evaluation.labels, evaluation.y_pred, title="Confusion Matrix", labels=labels, normalize=False,  save_path=save_path)

    # Optionally, save the evaluation results
    evaluation.save_evaluation()