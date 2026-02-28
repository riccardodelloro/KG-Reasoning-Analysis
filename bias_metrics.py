from utils import read_jsonl, compute_prior_bias, compute_context_bias

def main():
    models = ["nano", "standard"]
    methods = ["GCR", "RoG"]
    datasets = ["original", "slight", "significant", "comical", "uncomp"]

    for model in models:
        for method in methods:            
            path = f"results_detailed/{method}-{model}-detailed.jsonl"
            item_list = read_jsonl(path)

            #Compute prior bias for the original dataset and context bias for the altered datasets
            pb = compute_prior_bias(item_list, datasets[0])
            cbs = []
            for dataset in datasets[1:]:
                cb = compute_context_bias(item_list, dataset)
                cbs.append(cb)

            print(f"Model: {model}, Method: {method} -> Prior Bias: {pb:.0%}, Context Biases: {[f'{cb:.0%}' for cb in cbs]}")

if __name__ == "__main__":
    main()