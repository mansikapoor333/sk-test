"""
Variant C — Extend an Existing Pipeline
=========================================
You are given a WORKING evaluation pipeline below.
It already correctly computes precision, recall, accuracy, alignment_score.

Your task: add THREE new features without breaking anything existing.

Read the EXTENSION TASKS section at the bottom before writing any code.

Run: python working_pipeline.py   (should already produce valid output)
"""

import json
import csv
from collections import defaultdict

PASS = "pass"
NEEDS_REVISION = "needs_revision"


# ─── WORKING CODE (do not modify these functions) ────────────────────────────

def load_json(path):
    with open(path) as f:
        return json.load(f)

def load_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))

def normalize(response):
    try:
        parsed = json.loads(response)
        return ("json", json.dumps(parsed, sort_keys=True))
    except (json.JSONDecodeError, TypeError):
        return ("str", response.strip().lower())

def is_aligned(model_output, golden_response):
    return normalize(model_output) == normalize(golden_response)

def build_confusion_matrix(examples, model_outputs):
    gold = {e["id"]: e["label"] for e in examples}
    pred = {o["id"]: o["predicted_label"] for o in model_outputs}
    TP = FP = FN = TN = 0
    for id_, g in gold.items():
        p = pred[id_]
        if g == NEEDS_REVISION and p == NEEDS_REVISION: TP += 1
        elif g == PASS and p == NEEDS_REVISION:         FP += 1
        elif g == NEEDS_REVISION and p == PASS:         FN += 1
        else:                                           TN += 1
    return TP, FP, FN, TN

def compute_global_metrics(examples, model_outputs):
    TP, FP, FN, TN = build_confusion_matrix(examples, model_outputs)
    total = TP + FP + FN + TN
    gold_map   = {e["id"]: e["golden_response"] for e in examples}
    output_map = {o["id"]: o["output"] for o in model_outputs}
    aligned = sum(1 for id_ in gold_map if is_aligned(output_map[id_], gold_map[id_]))
    return {
        "precision":       round(TP / (TP + FP), 4) if (TP + FP) > 0 else 0.0,
        "recall":          round(TP / (TP + FN), 4) if (TP + FN) > 0 else 0.0,
        "accuracy":        round((TP + TN) / total, 4) if total > 0 else 0.0,
        "alignment_score": round(aligned / len(gold_map), 4) if gold_map else 0.0,
    }


# ─── EXTENSION TASKS ─────────────────────────────────────────────────────────
#
# The main() function below calls three stubs that you must implement.
# Do not modify main() or any of the working code above.
#
# TASK 1: domain_breakdown(examples, model_outputs)
#   - Group examples by the "domain" field
#   - For each domain compute: accuracy, recall, alignment_score, n (count)
#   - Add flag: underperforming = True if accuracy < 0.80
#   - Return: dict[domain -> {accuracy, recall, alignment_score, n, underperforming}]
#
# TASK 2: extract_false_negatives(examples, model_outputs)
#   - Return all examples where:
#       gold label = "needs_revision"  AND  predicted = "pass"
#   - These are the highest business risk (missed cases)
#   - Include fields: id, domain, golden_response, predicted_label
#
# TASK 3: f1_score(examples, model_outputs)
#   - Compute F1 = 2 * precision * recall / (precision + recall)
#   - Return 0.0 if denominator is 0
#   - Why F1? When classes are imbalanced, accuracy is misleading.
#     F1 balances precision and recall into a single number.
# ─────────────────────────────────────────────────────────────────────────────


def domain_breakdown(examples, model_outputs):
    # TODO: implement Task 1
    pass


def extract_false_negatives(examples, model_outputs):
    # TODO: implement Task 2
    pass


def f1_score(examples, model_outputs):
    # TODO: implement Task 3
    pass


# ─── SOLUTION (reveal after attempting) ──────────────────────────────────────

def domain_breakdown_SOLUTION(examples, model_outputs):
    gold_map   = {e["id"]: e for e in examples}
    output_map = {o["id"]: o for o in model_outputs}
    domain_ids = defaultdict(list)
    for e in examples:
        domain_ids[e["domain"]].append(e["id"])
    results = {}
    for domain, ids in domain_ids.items():
        d_ex  = [gold_map[i] for i in ids]
        d_out = [output_map[i] for i in ids]
        m = compute_global_metrics(d_ex, d_out)
        results[domain] = {
            "accuracy":        m["accuracy"],
            "recall":          m["recall"],
            "alignment_score": m["alignment_score"],
            "n":               len(ids),
            "underperforming": m["accuracy"] < 0.80,
        }
    return results

def extract_false_negatives_SOLUTION(examples, model_outputs):
    output_map = {o["id"]: o for o in model_outputs}
    return [
        {
            "id":              e["id"],
            "domain":          e["domain"],
            "golden_response": e["golden_response"],
            "predicted_label": output_map[e["id"]]["predicted_label"],
        }
        for e in examples
        if e["label"] == NEEDS_REVISION
        and output_map[e["id"]]["predicted_label"] == PASS
    ]

def f1_score_SOLUTION(examples, model_outputs):
    m = compute_global_metrics(examples, model_outputs)
    p, r = m["precision"], m["recall"]
    return round(2 * p * r / (p + r), 4) if (p + r) > 0 else 0.0


def main():
    examples      = load_csv("../variant_B_build/examples.csv")
    model_outputs = load_csv("../variant_B_build/model_outputs.csv")

    global_metrics = compute_global_metrics(examples, model_outputs)

    # Call your implementations (swap to _SOLUTION to check your work)
    breakdown  = domain_breakdown(examples, model_outputs)
    false_negs = extract_false_negatives(examples, model_outputs)
    f1         = f1_score(examples, model_outputs)

    print("=== Global Metrics ===")
    print(json.dumps(global_metrics, indent=2))
    print(f"\nF1 Score: {f1}")
    print("\n=== Domain Breakdown ===")
    print(json.dumps(breakdown, indent=2))
    print(f"\n=== False Negatives ({len(false_negs) if false_negs else 'NOT IMPLEMENTED'}) ===")
    if false_negs:
        for fn in false_negs:
            print(f"  {fn['id']} ({fn['domain']})")


if __name__ == "__main__":
    main()
