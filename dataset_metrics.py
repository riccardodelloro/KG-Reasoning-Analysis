from utils import read_jsonl, build_graph
import statistics
from collections import Counter

def get_q_entity_count(item):
    """
    Return the number of question entities in the question-item.
    If the 'q_entities' field is missing or not a list, return None.
    """
    q_entities = item.get("q_entity")
    if isinstance(q_entities, list):
        return len(q_entities)
    return None

def get_a_entity_count(item):
    """
    Return the number of answer entities in the question-item.
    If the 'a_entity' field is missing or not a list, return None.
    """
    a_entities = item.get("a_entity")
    if isinstance(a_entities, list):
        return len(a_entities)
    return None

def get_node_count(item):
    """
    Return the number of nodes in the graph of the question-item.
    If the 'graph' field is missing or not a list, return None.
    """
    graph_data = item.get("graph")
    if isinstance(graph_data, list):
        graph = build_graph(graph_data, undirected=False)
        return graph.number_of_nodes()
    return None

def get_edge_count(item):
    """
    Return the number of edges in the graph of the question-item.
    If the 'graph' field is missing or not a list, return None.
    """
    graph_data = item.get("graph")
    if isinstance(graph_data, list):
        graph = build_graph(graph_data, undirected=False)
        return graph.number_of_edges()
    return None

def get_dataset_type(item):
    """
    Return the dataset type from the question-item.
    """
    return [item.get("dataset")]

def get_stat_data_num(item_list, func):
    """
    Apply a function to each question-item and calculate statistics.
    The function may return:
      - None  -> ignored
      - int   -> single value
      - list[int] -> multiple values
    """
    values = []
    
    for item in item_list:
        result = func(item)
        if result is None:
            continue
        elif isinstance(result, int):
            values.append(result)
        else:
            continue

    if not values:
        print("No valid data available.")
        return
    
    mean_val = statistics.mean(values)
    median_val = statistics.median(values)
    
    print("Total sum:", sum(values))
    print("Mean:", mean_val)
    print("Median:", median_val)

def get_stat_data_cat(item_list, func):
    """
    Apply a function to each question-item and calculate categorical statistics.
    The function may return:
      - None       -> ignored
      - str        -> single category
      - list[str]  -> multiple categories
    """
    values = []

    for item in item_list:
        result = func(item)
        if result is None:
            continue
        elif isinstance(result, str):
            values.append(result)
        elif isinstance(result, list):
            values.extend([x for x in result if isinstance(x, str)])
        else:
            continue

    if not values:
        print("No valid categorical data available.")
        return
    
    distribution = Counter(values)
    
    print("Total count:", len(values))
    print("Distribution:")
    for val, count in distribution.most_common(10): 
        print(f"  {val}: {count}")

def main():
    path = "datasets/webqsp-original.jsonl"
    item_list = read_jsonl(path)

    print("Number of questions:", len(item_list))

    print("Answer count statistics:")
    get_stat_data_num(item_list, get_a_entity_count)
    print("\nQuestion entity count statistics:")
    get_stat_data_num(item_list, get_q_entity_count)
    print("\nNode count statistics:")
    get_stat_data_num(item_list, get_node_count)
    print("\nEdge count statistics:")
    get_stat_data_num(item_list, get_edge_count)
    print("\nDataset type statistics:")
    get_stat_data_cat(item_list, get_dataset_type)

if __name__ == "__main__":
    main()

    