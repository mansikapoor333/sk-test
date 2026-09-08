"""
Round 2 — SOLUTION (answer key, do not share with candidate)
"""

import csv
import json
from collections import defaultdict

PASS = "pass"
NEEDS_REVISION = "needs_revision"


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
        if g == NEEDS_REVISION and p == NEEDS_REVISION:
            TP += 1
        elif g == PASS and p == NEEDS_REVISION:
            FP += 1
        elif g == NEEDS_REVISION and p == PASS:
            FN += 1
        else:
            TN += 1
    return TP, FP, FN, TN


def compute_metrics(examples, model_outputs):
    TP, FP, FN, TN = build_confusion_matrix(examples, model_outputs)
    total = TP + FP + FN + TN

    precision      = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall         = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    acc            = (TP + TN) / total if total > 0 else 0.0

    gold_map   = {e["id"]: e["golden_response"] for e in examples}
    output_map = {o["id"]: o["output"] for o in model_outputs}
    aligned = sum(1 for id_ in gold_map if is_aligned(output_map[id_], gold_map[id_]))
    align_score = aligned / len(gold_map) if gold_map else 0.0

    return {
        "needs_revision_precision": round(precision, 4),
        "needs_revision_recall":    round(recall, 4),
        "accuracy":                 round(acc, 4),
        "alignment_score":          round(align_score, 4),
    }


def domain_breakdown(examples, model_outputs):
    gold_map   = {e["id"]: e for e in examples}
    output_map = {o["id"]: o for o in model_outputs}

    domain_ids = defaultdict(list)
    for e in examples:
        domain_ids[e["domain"]].append(e["id"])

    results = {}
    for domain, ids in domain_ids.items():
        d_examples = [gold_map[i] for i in ids]
        d_outputs  = [output_map[i] for i in ids]
        m = compute_metrics(d_examples, d_outputs)
        m["underperforming"] = m["accuracy"] < 0.80
        m["n"] = len(ids)
        results[domain] = m

    return results


def extract_false_negatives(examples, model_outputs):
    output_map = {o["id"]: o for o in model_outputs}
    return [
        {
            "id": e["id"],
            "domain": e["domain"],
            "label": e["label"],
            "predicted_label": output_map[e["id"]]["predicted_label"],
            "golden_response": e["golden_response"],
        }
        for e in examples
        if e["label"] == NEEDS_REVISION
        and output_map[e["id"]]["predicted_label"] == PASS
    ]


def interpret(global_metrics, breakdown, false_negatives):
    recall  = global_metrics["needs_revision_recall"]
    acc     = global_metrics["accuracy"]
    bad_domains = [d for d, v in breakdown.items() if v["underperforming"]]
    fn_count = len(false_negatives)

    s1 = f"The model achieves {acc:.0%} overall accuracy with strong precision on the needs_revision class."
    s2 = (
        f"However, recall is only {recall:.0%}, meaning {fn_count} cases that required revision "
        f"were missed entirely"
        + (f", with {', '.join(bad_domains)} showing accuracy below 80%." if bad_domains else ".")
    )
    s3 = (
        "The highest priority next step is a manual review of the false negatives to understand "
        "whether the errors share a pattern (e.g., a specific ICD code family or note style) "
        "that can be addressed with targeted labeling functions or fine-tuning data."
    )
    return f"{s1} {s2} {s3}"


def main():
    examples      = load_csv("examples.csv")
    model_outputs = load_csv("model_outputs.csv")

    global_metrics  = compute_metrics(examples, model_outputs)
    breakdown       = domain_breakdown(examples, model_outputs)
    false_negs      = extract_false_negatives(examples, model_outputs)
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
