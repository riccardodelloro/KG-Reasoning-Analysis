from utils import read_jsonl, compute_metrics, filter_by_one_correct_path

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

                adh, res, inc = compute_metrics(filtered_item_list, dataset)
                adh = adh / len(filtered_item_list)
                res = res / len(filtered_item_list)
                inc = inc / len(filtered_item_list)

                print(f"Model: {model}, Method: {method}, Dataset: {dataset} - Adh: {adh:.0%}, Res: {res:.0%}, Inc: {inc:.0%}")
            
if __name__ == "__main__":
    main()