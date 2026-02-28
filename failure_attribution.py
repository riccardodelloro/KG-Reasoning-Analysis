from utils import read_jsonl, compute_errors

def main():
    models = ["nano", "standard"]
    methods = ["GCR", "RoG"]
    datasets = ["original", "slight", "significant", "comical", "uncomp"]

    for model in models:
        for method in methods:            
            path = f"results_detailed/{method}-{model}-detailed.jsonl"
            item_list = read_jsonl(path)
            
            for dataset in datasets:
                err_tot, err_from_path, err_from_fa = compute_errors(item_list, dataset)

                print(f"Model: {model}, Method: {method}, Dataset: {dataset} - Err tot: {err_tot}, Err from Path: {err_from_path/err_tot:.0%}, Err from FA: {err_from_fa/err_tot:.0%}")

if __name__ == "__main__":
    main()