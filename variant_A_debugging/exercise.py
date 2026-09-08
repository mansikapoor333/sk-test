"""
Agent Evaluation Pipeline
=========================
This module evaluates model outputs against a golden dataset.

Positive class: "needs_revision"
Negative class: "pass"

Confusion matrix definitions:
  TP: gold = needs_revision, pred = needs_revision
  FP: gold = pass,           pred = needs_revision
  FN: gold = needs_revision, pred = pass
  TN: gold = pass,           pred = pass

Metrics:
  needs_revision_precision = TP / (TP + FP)   -- of all predicted positive, how many were correct
  needs_revision_recall    = TP / (TP + FN)   -- of all actual positive, how many did we catch
  accuracy                 = (TP + TN) / total
  alignment_score          = fraction of examples where model output matches golden_response

instruction_1 = '''
CONFUSION MATRIX REFERENCE

We are classifying examples into two classes:
  - Positive class: "needs_revision"
  - Negative class: "pass"

        Predicted NR    Predicted Pass
Gold NR     TP               FN
Gold Pass   FP               TN

TP (True Positive):  Gold is needs_revision, prediction is needs_revision. Correct catch.
FP (False Positive): Gold is pass, prediction is needs_revision. False alarm.
FN (False Negative): Gold is needs_revision, prediction is pass. Missed case (highest business risk).
TN (True Negative):  Gold is pass, prediction is pass. Correct dismissal.
'''

instruction_2 = '''
METRIC DEFINITIONS

needs_revision_precision: Of everything the model flagged as needing revision,
                          what fraction actually needed revision?
                          Formula: TP / (TP + FP). Return 0.0 if denominator is 0.

needs_revision_recall:    Of everything that actually needed revision,
                          what fraction did the model catch?
                          Formula: TP / (TP + FN). Return 0.0 if denominator is 0.

accuracy:                 Of all examples, what fraction were classified correctly?
                          Formula: (TP + TN) / total.

alignment_score:          Of all examples, what fraction of model outputs match the
                          golden response exactly (after normalization)?
                          Formula: aligned / total.
'''
"""

import json

PASS = "pass"
NEEDS_REVISION = "needs_revision"


def build_confusion_matrix(examples, model_outputs):
    """
    Build confusion matrix from examples and model_outputs.
    Returns (TP, FP, FN, TN).
    """
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
    # BUG 1: This computes recall for the PASS class, not the NEEDS_REVISION class.
    # Fix: change PASS -> NEEDS_REVISION in the denominator check, and use TP/(TP+FN)
    return TN / (TN + FP) if (TN + FP) > 0 else 0.0


def accuracy(examples, model_outputs):
    TP, FP, FN, TN = build_confusion_matrix(examples, model_outputs)
    total = TP + FP + FN + TN
    # BUG 2: Wrong numerator. This counts only TP, not TP+TN.
    # Fix: change TP -> (TP + TN)
    return TP / total if total > 0 else 0.0


def normalize(response):
    """
    Normalize a response for alignment comparison.
    BUG 3: Compares raw strings. JSON responses with different key ordering
           or whitespace will fail to match even when semantically identical.
    Fix: parse JSON first, then re-serialize with sort_keys=True.
    """
    return response.strip().lower()


def is_aligned(model_output, golden_response):
    """
    Returns True if model_output matches golden_response after normalization.
    """
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
    """Run the full evaluation and return all metrics."""
    return {
        "needs_revision_precision": needs_revision_precision(examples, model_outputs),
        "needs_revision_recall":    needs_revision_recall(examples, model_outputs),
        "accuracy":                 accuracy(examples, model_outputs),
        "alignment_score":          alignment_score(examples, model_outputs),
    }
