from utils import read_jsonl, count_no_existing_paths

def main():
    models = ["nano", "standard"]
    method = "ToG"
    datasets = ['original', 'slight', 'significant', 'comical', 'uncomp']

    for model in models:
        path = f"results_detailed/{method}-{model}-detailed.jsonl"
        item_list = read_jsonl(path)

        for dataset in datasets:    
            no_paths_count = count_no_existing_paths(item_list, dataset)
            
            print(f"Model: {model}, Dataset: {dataset} - No paths count: {no_paths_count}, {no_paths_count/len(item_list):.0%}")

if __name__ == "__main__":
    main()