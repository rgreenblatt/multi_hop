import sys
import json
from scipy import stats
import numpy as np

# path1, path2 = "eval_results/eval_results_opus3_r0.json", "eval_results/eval_results_opus3_r5.json"
path1, path2 = sys.argv[1], sys.argv[2]

with open(path1, "r") as f:
    data1 = json.loads(f.read())

with open(path2, "r") as f:
    data2 = json.loads(f.read())

print(data2["results"][0].keys())

assert [x["question"] for x in data1["results"]] == [x["question"] for x in data2["results"]]

correct1 = np.array([x["is_correct"] for x in data1["results"] if x["hops"] == 2]).astype(int)
correct2 = np.array([x["is_correct"] for x in data2["results"] if x["hops"] == 2]).astype(int)

# paired t-test
t_stat, p_value = stats.ttest_rel(correct1, correct2)

acc_diff = np.mean(correct2) - np.mean(correct1)

print(f"Accuracy 1: {np.mean(correct1):.4f}, Accuracy 2: {np.mean(correct2):.4f}")
print(f"Accuracy Difference: {acc_diff:.4f}")
print(f"Paired t-test: p-value = {p_value:.4f}")
