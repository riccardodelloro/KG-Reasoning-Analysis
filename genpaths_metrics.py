from utils import read_jsonl

def count_q_less_k_paths(item_list, dataset, k=3):
    """
    Count the number of questions that have less than k paths for the given dataset.
    """
    count = 0
    for item in item_list:
        if item[f"{dataset}_n_path"] < k:
            count += 1
    return count

def count_q_no_existing_paths(item_list, dataset):
    """
    Count the number of questions that have no existing paths for the given dataset.
    """
    count = 0
    for item in item_list:
        if item[f"{dataset}_path_existing"] == 0:
            count += 1
    return count

def count_q_no_correct_paths(item_list, dataset):
    """
    Count the number of questions that have no correct paths for the given dataset.
    """
    count = 0
    for item in item_list:
        if item[f"{dataset}_path_correct"] == 0:
            count += 1
    return count

def count_q_at_least_one_correct_path(item_list, dataset):
    """
    Count the number of questions that have at least one correct path for the given dataset.
    """
    count = 0
    for item in item_list:
        if item[f"{dataset}_path_correct"] >= 1:
            count += 1
    return count

def count_q_only_correct_paths(item_list, dataset):
    """
    Count the number of questions that have only correct paths (i.e., all paths are correct) for the given dataset.
    """
    count = 0
    for item in item_list:
        if item[f"{dataset}_n_path"] > 0 and item[f"{dataset}_n_path"] == item[f"{dataset}_path_correct"]:
            count += 1
    return count

def count_total_paths(item_list, dataset):
    """
    Count the total number of paths across all questions for the given dataset.
    """
    total = 0
    for item in item_list:
        total += item[f"{dataset}_n_path"]
    return total

def count_non_existing_paths(item_list, dataset):
    """
    Count the total number of non-existing paths across all questions for the given dataset.
    """
    total = 0
    for item in item_list:
        total += item[f"{dataset}_n_path"] - item[f"{dataset}_path_existing"]
    return total

def count_correct_paths(item_list, dataset):
    """
    Count the total number of correct paths across all questions for the given dataset.
    """
    total = 0
    for item in item_list:
        total += item[f"{dataset}_path_correct"]
    return total

def main():
    methods = ["GCR", "RoG"]
    datasets = ["original", "slight", "significant", "comical", "uncomp"]

    for method in methods:
        path = f"results_detailed/{method}-nano-detailed.jsonl"
        item_list = read_jsonl(path)

        for dataset in datasets:
            print(f"Method: {method}, Dataset: {dataset}")
            
            print("Total number of questions: ", len(item_list))
            print(f"Questions with less than 3 path: {count_q_less_k_paths(item_list, dataset)/len(item_list):.0%}")
            print(f"Questions without existing paths: {count_q_no_existing_paths(item_list, dataset)/len(item_list):.0%}")
            print(f"Questions without correct paths: {count_q_no_correct_paths(item_list, dataset)/len(item_list):.0%}")
            print(f"Questions with at least 1 correct path: {count_q_at_least_one_correct_path(item_list, dataset)/len(item_list):.0%}")
            print(f"Questions with only correct paths: {count_q_only_correct_paths(item_list, dataset)/len(item_list):.0%}")
            print("Total number of paths: ", count_total_paths(item_list, dataset))
            print(f"Non-existing paths: {count_non_existing_paths(item_list, dataset)/count_total_paths(item_list, dataset):.0%}")
            print(f"Correct paths: {count_correct_paths(item_list, dataset)/count_total_paths(item_list, dataset):.0%}")

if __name__ == "__main__":
    main()