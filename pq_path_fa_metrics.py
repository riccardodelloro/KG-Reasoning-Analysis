from utils import read_jsonl, filter_by_one_correct_path, filter_by_pq_correct, filter_by_pq_incorrect, compute_metrics

def main():
    models = ["nano", "standard"]
    methods = ["GCR", "RoG"]
    datasets = ["original", "slight", "significant", "comical", "uncomp"]

    for model in models:
        for method in methods:            
            path = f"results_detailed/{method}-{model}-detailed.jsonl"
            item_list = read_jsonl(path)
            for dataset in datasets:
                filtered_item_list = filter_by_one_correct_path(item_list, dataset)
                filtered_item_list_pq_correct = filter_by_pq_correct(filtered_item_list)
                filtered_item_list_pq_incorrect = filter_by_pq_incorrect(filtered_item_list)

                adh_pq_correct, res_pq_correct, _ = compute_metrics(filtered_item_list_pq_correct, dataset)
                adh_pq_correct = adh_pq_correct / len(filtered_item_list_pq_correct)
                res_pq_correct = res_pq_correct / len(filtered_item_list_pq_correct)
                adh_pq_incorrect, _, _ = compute_metrics(filtered_item_list_pq_incorrect, dataset)
                adh_pq_incorrect = adh_pq_incorrect / len(filtered_item_list_pq_incorrect)

                print(f"Model: {model}, Method: {method}, Dataset: {dataset} - Adh_pq_cor: {adh_pq_correct:.0%}, Res_pq_cor: {res_pq_correct:.0%}, Adh_pq_inc: {adh_pq_incorrect:.0%}")

if __name__ == "__main__":
    main()