"""
exercise_SOLUTION.py — ANSWER KEY (do not share with candidate)
===============================================================
Three bugs fixed, each a 1-word or 1-line change:

  Bug 1 (line ~60): needs_revision_recall computed for PASS class.
         Fix: return TP / (TP + FN)  [was TN / (TN + FP)]

  Bug 2 (line ~68): accuracy numerator was TP only.
         Fix: return (TP + TN) / total  [was TP / total]

  Bug 3 (line ~77): normalize() used raw string comparison.
         Fix: try json.loads -> json.dumps(sort_keys=True), fall back to strip().lower()
"""

import json

PASS = "pass"
NEEDS_REVISION = "needs_revision"


def build_confusion_matrix(examples, model_outputs):
    gold = {e["id"]: e["label"] for e in examples}
    pred = {o["id"]: o["predicted_label"] for o in model_outputs}
    TP = FP = FN = TN = 0
    for id_, g in gold.items():
        p = pred[id_]
        if g == NEEDS_REVISION and p == NEEDS_REVISION:
            TP += 1
        elif g == PASS and p == NEEDS_REVISION:
            FP += 1
        elif g == NEEDS_REVISION and p == PASS:
            FN += 1
        else:
            TN += 1
    return TP, FP, FN, TN


def needs_revision_precision(examples, model_outputs):
    TP, FP, FN, TN = build_confusion_matrix(examples, model_outputs)
    return TP / (TP + FP) if (TP + FP) > 0 else 0.0


def needs_revision_recall(examples, model_outputs):
    TP, FP, FN, TN = build_confusion_matrix(examples, model_outputs)
    # FIX 1: was TN / (TN + FP) — that's recall for the PASS class
    return TP / (TP + FN) if (TP + FN) > 0 else 0.0


def accuracy(examples, model_outputs):
    TP, FP, FN, TN = build_confusion_matrix(examples, model_outputs)
    total = TP + FP + FN + TN
    # FIX 2: was TP / total — missing TN in numerator
    return (TP + TN) / total if total > 0 else 0.0


def normalize(response):
    # FIX 3: was return response.strip().lower() — misses JSON key-ordering differences
    try:
        parsed = json.loads(response)
        return ("json", json.dumps(parsed, sort_keys=True))
    except (json.JSONDecodeError, TypeError):
        return ("str", response.strip().lower())


def is_aligned(model_output, golden_response):
    # Tuple comparison: type tag prevents ("json", x) == ("str", x)
    return normalize(model_output) == normalize(golden_response)


def alignment_score(examples, model_outputs):
    gold = {e["id"]: e["golden_response"] for e in examples}
    outputs = {o["id"]: o["output"] for o in model_outputs}
    aligned = sum(
        1 for id_ in gold
        if is_aligned(outputs[id_], gold[id_])
    )
    return aligned / len(gold) if gold else 0.0


def run_evaluation(examples, model_outputs):
    return {
        "needs_revision_precision": needs_revision_precision(examples, model_outputs),
        "needs_revision_recall":    needs_revision_recall(examples, model_outputs),
        "accuracy":                 accuracy(examples, model_outputs),
        "alignment_score":          alignment_score(examples, model_outputs),
    }
