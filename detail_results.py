from utils import write_jsonl, check_answer_match, analyze_prediction, is_path_correct, is_path_existing, build_graph
import json
from contextlib import ExitStack

def analyze_predictions(predictions, answer_original, answer_modified):
    """
    For a list of predictions, categorize each prediction as adherent, resistant, or incorrect,
    and return the count for each category.
    """
    adherence_count = 0  
    resistance_count = 0  
    incorrectness_count = 0  

    for prediction in predictions:
        category = analyze_prediction(prediction, answer_original, answer_modified)
        if category == "ADH":
            adherence_count += 1
        elif category == "RES":
            resistance_count += 1
        else:
            incorrectness_count += 1

    return adherence_count, resistance_count, incorrectness_count

def jsonl_iter(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def process_item(pq, datasets_dict, results_dict, method):
    """
    For each question-item, compute adherence, resistance, and incorrectness counts for the PQ method and for each dataset, 
    as well as path correctness and existence counts for each dataset.
    For ToG, path correctness is set to 0 and path existence is set to the total number of generated paths.
    """
    
    datasets = ['original', 'slight', 'significant', 'comical', 'uncomp']

    id = pq['id']
    n_answers = len(datasets_dict['original']['a_entity'])
    
    strict_match = False
    pq_n_pred = len(pq['prediction'])
    pq_adh = 0
    for pred in pq['prediction']:
        for a_entity in datasets_dict['original']['a_entity']:
            if check_answer_match(pred, a_entity, strict = strict_match):
                pq_adh += 1
                break
    pq_inc = pq_n_pred - pq_adh

    result = {
        "id": id,
        "n_answers": n_answers,
        "pq_n_pred": pq_n_pred,
        "pq_adh": pq_adh,
        "pq_res": 0,
        "pq_inc": pq_inc,
    }

    for dataset in datasets:
        result[f"{dataset}_n_pred"]= len(results_dict[dataset]['prediction'])
        adh, res, inc = analyze_predictions(
            results_dict[dataset]['prediction'],
            datasets_dict['original']['answer'],
            datasets_dict[dataset]['answer']
        )
        result[f"{dataset}_adh"] = adh
        result[f"{dataset}_res"] = res
        result[f"{dataset}_inc"] = inc
        
        result[f"{dataset}_n_path"] = len(results_dict[dataset]['gen_paths'])
        path_correct = 0
        path_existing = 0
        q_entity = datasets_dict[dataset]['q_entity']
        if method == "ToG":
            result[f"{dataset}_path_existing"] = len(results_dict[dataset]['gen_paths'])
            result[f"{dataset}_path_correct"] = 0
        else:
            G = build_graph(datasets_dict[dataset]['graph'], undirected=True)
            for path in results_dict[dataset]['gen_paths']:
                if is_path_correct(path, results_dict[dataset]['ground_paths']):
                    path_correct += 1
                if is_path_existing(path, G, q_entity, method=method):
                    path_existing += 1
            result[f"{dataset}_path_correct"] = path_correct
            result[f"{dataset}_path_existing"] = path_existing

    return result

def main():
    datasets_names = ["original", "slight", "significant", "comical", "uncomp"]
    models = ["nano", "standard"]
    methods = ["GCR", "RoG", "ToG"]

    n_item_standard = 86
    n_item_nano = 1462

    for method in methods:
        for model in models:
            print(f"Processing method '{method}' and model '{model}'...")
            res_list = []
            n_item = n_item_standard if model == "standard" else n_item_nano

            dataset_paths = {d: f"datasets/webqsp-{d}.jsonl" for d in datasets_names}
            results_paths = {d: f"results/{method}-{model}-{d}.jsonl" for d in datasets_names}
            pq_path = f"results/pq-{model}-original.jsonl"

            with ExitStack() as stack:
                dataset_files = {d: stack.enter_context(open(p, "r", encoding="utf-8")) for d, p in dataset_paths.items()}
                results_files = {d: stack.enter_context(open(p, "r", encoding="utf-8")) for d, p in results_paths.items()}
                pq_file = stack.enter_context(open(pq_path, "r", encoding="utf-8"))

                for i in range(n_item):
                    datasets_dict = {d: json.loads(dataset_files[d].readline()) for d in datasets_names}
                    results_dict = {d: json.loads(results_files[d].readline()) for d in datasets_names}
                    pq = json.loads(pq_file.readline())

                    result = process_item(pq, datasets_dict, results_dict, method)
                    res_list.append(result)

            write_jsonl(res_list, f"results_detailed/{method}-{model}-detailed.jsonl")

if __name__ == "__main__":
    main()