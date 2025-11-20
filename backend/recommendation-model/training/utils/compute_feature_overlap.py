import numpy as np

# compute the feature item overlap between two sets for use in reranker 
def compute_set_overlap(list1: list, list2: list) -> np.ndarray:
    overlaps = []
    for s1, s2 in zip(list1, list2):
        set1 = set(s1.split('|')) if s1 else set()
        set2 = set(s2.split('|')) if s2 else set()
        overlaps.append(len(set1 & set2))
    return np.array(overlaps, dtype=np.float32)