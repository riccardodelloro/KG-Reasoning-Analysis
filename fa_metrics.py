from utils import read_jsonl, compute_metrics, compute_metrics_pq

def main():
    models = ["nano", "standard"]
    methods = ["GCR", "RoG"]
    datasets = ["original", "slight", "significant", "comical", "uncomp"]

    for model in models:
        path = f"results_detailed/GCR-{model}-detailed.jsonl"
        item_list = read_jsonl(path)

        pq_adh, pq_res, pq_inc = compute_metrics_pq(item_list)
        pq_adh = pq_adh / len(item_list)
        pq_res = pq_res / len(item_list)
        pq_inc = pq_inc / len(item_list)

        print(f"Model: {model}, Method: PQ, Dataset: Original - Adh: {pq_adh:.0%}, Res: {pq_res:.0%}, Inc: {pq_inc:.0%}")

        for method in methods:            
            path = f"results_detailed/{method}-{model}-detailed.jsonl"
            item_list = read_jsonl(path)

            for dataset in datasets:
                adh, res, inc = compute_metrics(item_list, dataset)
                adh = adh / len(item_list)
                res = res / len(item_list)
                inc = inc / len(item_list)
                
                print(f"Model: {model}, Method: {method}, Dataset: {dataset} - Adh: {adh:.0%}, Res: {res:.0%}, Inc: {inc:.0%}")

if __name__ == "__main__":
    main()