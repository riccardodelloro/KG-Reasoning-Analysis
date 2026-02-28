import json
import networkx as nx
from collections import deque
import statistics
from collections import Counter
import random
import gc
from typing import List, Dict, Any
import json

def read_jsonl(file_path):
    """
    Read a JSONL file and return a list of JSON objects.
    """
    objects = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if line:  
                    try:
                        json_obj = json.loads(line)
                        objects.append(json_obj)
                    except json.JSONDecodeError as e:
                        print(f"Error in line {line_number}: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        raise
    
    return objects

def write_jsonl(json_objects, filename):
    """
    Write a list of JSON objects to a JSONL file, one object per line.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for obj in json_objects:
            json.dump(obj, f, ensure_ascii=False)
            f.write('\n')

def check_answer_match(prediction, answer, strict=True):
    """
    Check if two answers can be considered matching. 
    If strict is True, the answers must match exactly.
    If strict is False, the answers are considered matching if one is a substring of the other.
    """
    if strict:
        return prediction.strip().lower() == answer.strip().lower()
    else:
        return answer.strip().lower() in prediction.strip().lower() or prediction.strip().lower() in answer.strip().lower()
    
def build_graph(graph: list, undirected = False) -> nx.DiGraph | nx.Graph:
    """
    Build a NetworkX graph from a list of triplets. Each triplet is expected to be in the form [head, relation, tail].
    """
    if undirected:
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    for triplet in graph:
        h, r, t = triplet
        edge = G.get_edge_data(h.strip(), t.strip(), default=None)
        if edge is None:
            G.add_edge(h.strip(), t.strip(), relation=[r.strip()])
        else:
            relations = edge.get('relation')
            relations.append(r.strip())
            G.add_edge(h.strip(), t.strip(), relation=relations)
    return G

def analyze_prediction(prediction, answer_original, answer_modified):
    """
    Analyze a single prediction and categorize it as adherent, resistant, or incorrect.
    A prediction is adherent (ADH) if it matches any of the modified answers, 
    resistant (RES) if it matches any of the original answers, 
    and incorrect (INC) otherwise.
    """
    for modified_answer in answer_modified: 
        if check_answer_match(prediction, modified_answer, strict=True):
            return "ADH"
    for original_answer in answer_original:
        if check_answer_match(prediction, original_answer, strict=True):
            return "RES"
    for modified_answer in answer_modified: 
        if check_answer_match(prediction, modified_answer, strict=False):
            return "ADH"
    for original_answer in answer_original:
        if check_answer_match(prediction, original_answer, strict=False):
            return "RES"
    return "INC"

def is_path_correct(path, ground_paths):
    """ 
    Check if a predicted path is correct by comparing it to the ground truth paths.
    A predicted path is considered correct if any of the ground truth paths is a subsequence of the predicted path.
    """
    path  = "".join(path)
    for gp in ground_paths:
        gp = "".join(gp)
        if gp in path:
            return True
    return False

def is_path_existing(path, graph, q_entity, method):
    """
    Check if a predicted path exists on the graph starting from any of the question entities, 
    according to the specified method (GCR or RoG).
    """
    path = path.split(" -> ")

    if method == "GCR":
        return any(path_exists_on_graph_gcr(graph, path, entity) for entity in q_entity)
    elif method == "RoG":
        return any(path_exists_on_graph_rog(graph, path, entity) for entity in q_entity)
    return False

def path_exists_on_graph_gcr(graph: nx.Graph, path: List[str], start: str) -> bool:
    """
    Check if a reasoning path exists on the graph starting from a specific node.
    The path is in the form [entity, relation, entity, relation, ...]
    """
    if len(path) < 3 or len(path) % 2 == 0:
        return False
    
    entities = [path[i] for i in range(0, len(path), 2)]
    
    for entity in entities:
        if entity not in graph.nodes():
            return False
        
    if entities[0] != start:
        return False
    
    for i in range(len(entities) - 1):
        entity1 = entities[i]
        entity2 = entities[i + 1]
        expected_relation = path[2 * i + 1]  # La relazione tra le due entità
        
        if not graph.has_edge(entity1, entity2):
            return False
        
        edge_data = graph.get_edge_data(entity1, entity2)
        if edge_data and 'relation' in edge_data:
            if expected_relation not in edge_data['relation']:
                return False
    
    return True

def path_exists_on_graph_rog(graph: nx.Graph, path: List[str], start: str) -> bool:
    """
    Check if a relation path exists on the graph starting from a specific node.
    The path is in the form [relation, relation, relation, ...]
    """
    if start not in graph:
        return False
    
    if path == []:
        return True
    
    connected_nodes = []
    for neighbor in graph.neighbors(start):
        edge_data = graph.get_edge_data(start, neighbor)
        if edge_data and path[0] in edge_data.get('relation'):
            connected_nodes.append(neighbor)

    if not connected_nodes:
        return False

    for next_node in connected_nodes:
        if path_exists_on_graph_rog(graph, path[1:], next_node):
            return True
    return False 

#######################################################################
# Following functions are used to analyze items from detailed_results #
#######################################################################

def compute_metrics(item_list, dataset):
    """
    Compute the total sum of adherence, resistance, and hallucination for the given dataset.
    """
    adh, res, inc = 0, 0, 0
    for item in item_list:
        adh += item[f"{dataset}_adh"]
        res += item[f"{dataset}_res"]
        inc += item[f"{dataset}_inc"]
    return adh, res, inc

def compute_metrics_pq(item_list):
    """
    Compute the total sum of adherence, resistance, and hallucination for the PQ method.
    """
    adh, res, inc = 0, 0, 0
    for item in item_list:
        adh += item["pq_adh"]
        res += item["pq_res"]
        inc += item["pq_inc"]
    return adh, res, inc

def compute_errors(item_list, dataset):
    """
    Compute the total number of errors, the number of errors attributable to path issues, and the number of errors attributable to FA issues for the given dataset.
    """
    err_tot, err_from_path, err_from_fa = 0, 0, 0
    for item in item_list:
        if item[f"{dataset}_adh"] == 0:
            err_tot += 1
            if item[f"{dataset}_path_correct"] == 0:
                err_from_path += 1
            else:
                err_from_fa += 1
    return err_tot, err_from_path, err_from_fa

def filter_by_one_correct_path(item_list, dataset):
    """
    Filter the question-items to include only those that have at least one correct path for the given dataset.
    """
    filtered_list = []
    for item in item_list:
        if item[f"{dataset}_path_correct"] >= 1:
            filtered_list.append(item)
    return filtered_list

def filter_by_one_existing_path(item_list, dataset):
    """
    Filter the question-items to include only those that have at least one existing path for the given dataset.
    """
    filtered_list = []
    for item in item_list:
        if item[f"{dataset}_path_existing"] >= 1:
            filtered_list.append(item)
    return filtered_list

def filter_by_pq_correct(item_list):
    """
    Filter the question-items to include only those for which PQ method gave a correct result (i.e., pq_adh == 1).
    """
    filtered_list = []
    for item in item_list:
        if item[f"pq_adh"] == 1:
            filtered_list.append(item)
    return filtered_list

def filter_by_pq_incorrect(item_list):
    """
    Filter the question-items to include only those for which PQ method gave an incorrect result (i.e., pq_adh == 0).
    """
    filtered_list = []
    for item in item_list:
        if item[f"pq_adh"] == 0:
            filtered_list.append(item)
    return filtered_list

def compute_prior_bias(item_list, dataset):
    """
    Compute prior bias for the given dataset (should be Original dataset).
    """
    item_list_filtered = filter_by_one_correct_path(item_list, dataset)
    item_list_filtered_pq_incorrect = filter_by_pq_incorrect(item_list_filtered)
    inc = 0
    for item in item_list_filtered_pq_incorrect:
        inc += item[f"{dataset}_inc"]
    inc = inc / len(item_list_filtered_pq_incorrect)
    return inc

def compute_context_bias(item_list, dataset):
    """
    Compute context bias for the given dataset (should be an altered dataset).
    """
    item_list_filtered = filter_by_one_correct_path(item_list, dataset)
    item_list_filtered_pq_correct = filter_by_pq_correct(item_list_filtered)
    adh = 0
    for item in item_list_filtered_pq_correct:
        adh += item[f"{dataset}_adh"]
    adh = adh / len(item_list_filtered_pq_correct)
    return adh

def count_no_existing_paths(item_list, dataset):
    """
    Count the number of questions that have no existing paths for the given dataset.
    """
    count = 0
    for item in item_list:
        if item[f"{dataset}_path_existing"] == 0:
            count += 1
    return count
