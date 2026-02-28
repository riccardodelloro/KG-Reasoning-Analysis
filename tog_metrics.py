from utils import read_jsonl, compute_metrics, filter_by_one_existing_path

def main():
    models = ["nano", "standard"]
    method = "ToG"
    datasets = ["original", "slight", "significant", "comical", "uncomp"]

    for model in models:
        path = f"results_detailed/{method}-{model}-detailed.jsonl"
        item_list = read_jsonl(path)

        for dataset in datasets:    
            item_list_filtered = filter_by_one_existing_path(item_list, dataset)

            adh, res, inc = compute_metrics(item_list_filtered, dataset)
            tot = adh + res + inc
            adh = adh / tot
            res = res / tot
            inc = inc / tot
            count_one_existing_path = len(item_list_filtered) / len(item_list)

            print(f"Model: {model}, Dataset: {dataset} - Q_one_path: {count_one_existing_path:.0%} - Adh: {adh:.0%}, Res: {res:.0%}, Inc: {inc:.0%}")

if __name__ == "__main__":
    main()