"""
Round 2 — Build the Evaluation Pipeline
========================================
Read client_brief.md first. Seriously. Read it.

Then read examples.csv and model_outputs.csv to understand the data shape.

Your task: implement the four functions below so that main() produces
a correct JSON report and 3-sentence interpretation.

Rules:
  - Positive class = "needs_revision"
  - TP: gold=needs_revision, pred=needs_revision
  - FP: gold=pass,           pred=needs_revision
  - FN: gold=needs_revision, pred=pass
  - TN: gold=pass,           pred=pass

  - Precision = TP / (TP+FP), 0.0 if denom is 0
  - Recall    = TP / (TP+FN), 0.0 if denom is 0
  - Accuracy  = (TP+TN) / total
  - Alignment: JSON responses -> compare parsed structures, not raw strings
               Plain strings  -> compare strip().lower()

Run: python starter.py
"""

import csv
import json
from collections import defaultdict

PASS = "pass"
NEEDS_REVISION = "needs_revision"


# ── helpers ──────────────────────────────────────────────────────────────────

def load_csv(path):
    """Load a CSV file and return a list of dicts."""
    with open(path) as f:
        return list(csv.DictReader(f))


def normalize(response):
    """
    Normalize a response for alignment comparison.
    If valid JSON: return canonical form (sorted keys).
    Otherwise: return strip().lower().
    Hint: use a tuple so ("json", x) != ("str", x) even if x looks the same.
    """
    # TODO
    pass


def is_aligned(model_output, golden_response):
    """Return True if model_output matches golden_response after normalization."""
    # TODO
    pass


# ── metrics ──────────────────────────────────────────────────────────────────

def build_confusion_matrix(examples, model_outputs):
    """
    Build a confusion matrix.
    Returns (TP, FP, FN, TN) as integers.
    Tip: build lookup dicts first, then iterate over gold IDs.
    """
    # TODO
    pass


def compute_metrics(examples, model_outputs):
    """
    Compute all four metrics.
    Returns dict with keys:
      needs_revision_precision, needs_revision_recall, accuracy, alignment_score
    """
    # TODO
    pass


# ── per-domain breakdown ──────────────────────────────────────────────────────

def domain_breakdown(examples, model_outputs):
    """
    Group examples by domain. For each domain, compute metrics.
    Flag underperforming: True if accuracy < 0.80.
    Returns dict[domain -> {precision, recall, accuracy, alignment_score,
                             underperforming, n}]
    """
    # TODO
    pass


# ── false negatives ───────────────────────────────────────────────────────────

def extract_false_negatives(examples, model_outputs):
    """
    Return list of examples where:
      gold label = needs_revision
      predicted  = pass
    These are highest business risk (missed cases).
    """
    # TODO
    pass


# ── report ────────────────────────────────────────────────────────────────────

def interpret(global_metrics, breakdown, false_negatives):
    """
    Write 3 sentences:
      1. What is the model doing well?
      2. Where is it failing?
      3. Single most important next step.
    """
    # TODO
    return "Interpretation goes here."


def main():
    examples       = load_csv("examples.csv")
    model_outputs  = load_csv("model_outputs.csv")

    global_metrics = compute_metrics(examples, model_outputs)
    breakdown      = domain_breakdown(examples, model_outputs)
    false_negs     = extract_false_negatives(examples, model_outputs)
    underperforming = [d for d, v in breakdown.items() if v.get("underperforming")]

    report = {
        "global": global_metrics,
        "per_domain": breakdown,
        "underperforming_domains": underperforming,
        "false_negative_count": len(false_negs),
        "false_negative_ids": [fn["id"] for fn in false_negs],
    }

    print(json.dumps(report, indent=2))
    print("\n--- interpretation ---")
    print(interpret(global_metrics, breakdown, false_negs))


if __name__ == "__main__":
    main()
