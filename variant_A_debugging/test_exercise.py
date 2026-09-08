"""
test_exercise.py
================
Three failing tests. Your job: fix exercise.py so all three pass.
DO NOT modify this file. The tests are correct. The bugs are in exercise.py.

Run with: python -m pytest test_exercise.py -v
Or:        python test_exercise.py
"""

import json
import sys

try:
    from exercise import (
        needs_revision_recall,
        accuracy,
        alignment_score,
        run_evaluation,
        needs_revision_precision,
    )
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Load dataset
# ---------------------------------------------------------------------------
with open("examples.json") as f:
    examples = json.load(f)

# Scenario A: model predicts everything as PASS (all FN, no FP)
# Buggy recall = TN/(TN+FP) = 0/0 -> 0.0 (returns 0, but correct is also 0 here)
# We need a case where buggy != correct AND test threshold exposes the bug clearly.

# Scenario B: model predicts everything CORRECTLY except 2 FNs
# Correct recall = TP/(TP+FN) = 6/8 = 0.75
# Buggy recall   = TN/(TN+FP) = 8/8 = 1.0  <-- BUG: returns 1.0, test asserts < 1

fn_ids_recall = {"4", "14"}  # gold=needs_revision, pred=pass -> creates FNs, 0 FPs

model_outputs_recall = []
for e in examples:
    if e["id"] in fn_ids_recall:
        predicted = "pass"
    else:
        predicted = e["label"]   # everything else correct, 0 FPs
    model_outputs_recall.append({
        "id": e["id"],
        "predicted_label": predicted,
        "output": e["golden_response"],
    })

# Scenario C: model with some errors for accuracy test
fn_ids_acc = {"4", "14"}
fp_ids_acc = {"11"}

model_outputs_acc = []
for e in examples:
    if e["id"] in fn_ids_acc:
        predicted = "pass"
    elif e["id"] in fp_ids_acc:
        predicted = "needs_revision"
    else:
        predicted = e["label"]
    model_outputs_acc.append({
        "id": e["id"],
        "predicted_label": predicted,
        "output": e["golden_response"],
    })

# Scenario D: JSON outputs with shuffled keys for alignment test
model_outputs_align = []
for e in examples:
    out = e["golden_response"]
    if out.startswith("{"):
        try:
            parsed = json.loads(out)
            out = json.dumps(dict(reversed(list(parsed.items()))))
        except Exception:
            pass
    model_outputs_align.append({
        "id": e["id"],
        "predicted_label": e["label"],
        "output": out,
    })


# ---------------------------------------------------------------------------
# Test 1: needs_revision_recall < 1 when there are false negatives and zero FPs
# ---------------------------------------------------------------------------
def test_needs_revision_recall_less_than_1():
    """
    Model correctly labels everything EXCEPT 2 needs_revision examples (FNs).
    Zero false positives (FP=0).

    Buggy formula:  TN / (TN + FP) = 8 / (8 + 0) = 1.0  <- FAILS this test
    Correct formula: TP / (TP + FN) = 6 / (6 + 2) = 0.75 <- PASSES this test

    If you get 1.0, your recall is computing the wrong class.
    Fix: use TP/(TP+FN), not TN/(TN+FP).
    """
    result = needs_revision_recall(examples, model_outputs_recall)
    assert result < 1, (
        f"recall should be < 1 (got {result:.4f}). "
        f"Check you're computing TP/(TP+FN), not TN/(TN+FP)."
    )


# ---------------------------------------------------------------------------
# Test 2: accuracy > 0.75 with most examples correct
# ---------------------------------------------------------------------------
def test_accuracy():
    """
    3 mis-classifications out of 16 examples.
    Correct: (TP+TN)/total = 13/16 = 0.8125
    Buggy:   TP/total      =  6/16 = 0.375   <- FAILS this test

    If you get ~0.375, your numerator is TP only (missing TN).
    Fix: use (TP + TN) / total.
    """
    result = accuracy(examples, model_outputs_acc)
    assert result > 0.75, (
        f"accuracy should be > 0.75 (got {result:.4f}). "
        f"Check your numerator is (TP + TN), not just TP."
    )


# ---------------------------------------------------------------------------
# Test 3: alignment_score > 0.5 when JSON keys are shuffled
# ---------------------------------------------------------------------------
def test_alignment_score():
    """
    All model outputs are semantically correct, but JSON responses have
    reversed key order e.g. {"description": "...", "icd_code": "..."}.

    Buggy:   string compare -> 0 JSON matches  = 8/16 = 0.5 (only plain strings match)
    Correct: json.loads compare -> all match   = 16/16 = 1.0

    If you get ~0.5625, you're comparing raw strings instead of parsed JSON.
    Fix: try json.loads on both sides, then compare the parsed structures.
    """
    result = alignment_score(examples, model_outputs_align)
    assert result > 0.6, (
        f"alignment_score should be > 0.6 (got {result:.4f}). "
        f"JSON responses with different key ordering should still be considered aligned. "
        f"Fix: normalize via json.loads + json.dumps(sort_keys=True)."
    )


# ---------------------------------------------------------------------------
# Bonus: smoke test
# ---------------------------------------------------------------------------
def test_run_evaluation_keys():
    result = run_evaluation(examples, model_outputs_acc)
    expected = {"needs_revision_precision", "needs_revision_recall",
                "accuracy", "alignment_score"}
    assert expected == set(result.keys())
    for k, v in result.items():
        assert 0.0 <= v <= 1.0, f"{k}={v} out of range"


# ---------------------------------------------------------------------------
# Run manually if not using pytest
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    tests = [
        ("test_needs_revision_recall_less_than_1", test_needs_revision_recall_less_than_1),
        ("test_accuracy", test_accuracy),
        ("test_alignment_score", test_alignment_score),
        ("test_run_evaluation_keys", test_run_evaluation_keys),
    ]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {name}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
