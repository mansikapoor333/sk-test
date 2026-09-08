# Variant A — Debugging Hints (use in order, peek only when stuck)

Run first: python test_exercise.py
You will see 3 failures. Fix exercise.py only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUG 1 — test_needs_revision_recall_less_than_1 FAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HINT 1: Read instruction_2 in exercise.py. What is the formula for recall?

HINT 2: Find the needs_revision_recall() function. What formula is it
        currently using? Write it out: numerator / denominator.

HINT 3: The current code returns TN / (TN + FP).
        TN = true negatives (gold=pass, pred=pass).
        That is recall for the PASS class, not the NEEDS_REVISION class.

HINT 4: Recall for needs_revision = TP / (TP + FN).
        Change exactly one variable name in the return statement.

FIX (1 word change):
  BEFORE: return TN / (TN + FP) if (TN + FP) > 0 else 0.0
  AFTER:  return TP / (TP + FN) if (TP + FN) > 0 else 0.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUG 2 — test_accuracy FAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HINT 1: Read instruction_2. Accuracy formula = (TP + TN) / total.

HINT 2: Find accuracy() function. What is in the numerator right now?

HINT 3: The numerator is just TP. That only counts correctly-caught
        "needs_revision" cases. It misses TN (correctly-caught "pass" cases).

HINT 4: A model that correctly predicts 7 "pass" examples (TN=7) but the
        code ignores all of them — accuracy will look much lower than reality.

FIX (2 words added):
  BEFORE: return TP / total if total > 0 else 0.0
  AFTER:  return (TP + TN) / total if total > 0 else 0.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUG 3 — test_alignment_score FAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HINT 1: Find normalize(). What does it currently return?

HINT 2: Some golden_responses are JSON strings like:
        {"icd_code": "I10", "description": "Essential hypertension"}
        The model output might be:
        {"description": "Essential hypertension", "icd_code": "I10"}
        Same content, different key order. strip().lower() makes them unequal.

HINT 3: You need to compare the parsed structure, not the raw string.
        What Python module parses JSON strings?

HINT 4: json.loads() parses a JSON string into a dict.
        json.dumps(parsed, sort_keys=True) produces a canonical string.
        Two dicts with the same keys+values will produce the same canonical string.

HINT 5: Wrap in try/except — not everything is valid JSON.
        If json.loads() raises an exception, fall back to strip().lower().

FIX (replace the normalize function body):
  try:
      parsed = json.loads(response)
      return ("json", json.dumps(parsed, sort_keys=True))
  except (json.JSONDecodeError, TypeError):
      return ("str", response.strip().lower())

  NOTE: The tuple ("json", ...) vs ("str", ...) ensures that a JSON value
  and a plain string with the same text are never considered equal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT TO SAY WHEN YOU FIND EACH BUG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bug 1: "The test expects recall < 1, meaning we have false negatives.
        The current formula is TN/(TN+FP) — that's recall for the pass class.
        Recall for needs_revision should be TP/(TP+FN). One word change."

Bug 2: "The test expects accuracy > 0.75 but we're getting ~0.37.
        The numerator is just TP — it's ignoring all the correctly-predicted
        pass examples. Accuracy needs TP+TN in the numerator."

Bug 3: "Alignment is too low because some golden responses are JSON strings.
        The model output might have the same keys in different order.
        String comparison fails. I need to normalize both through json.loads
        so I'm comparing parsed structures, not raw text."
