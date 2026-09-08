# Client Brief — Model Evaluation Engagement

## Background

A Fortune 500 healthcare company has deployed an LLM to assist medical coders in
classifying patient diagnoses. The model receives a free-text clinical note and
produces two outputs:

1. A predicted label: `"pass"` (coding looks correct) or `"needs_revision"` (coding needs human review)
2. A structured JSON response with the suggested ICD code and description

The company's QA team has manually reviewed 200 examples and produced a golden
dataset. They've also captured 200 model outputs for the same examples.

Your job: build the evaluation pipeline, report metrics, identify failures, and
give the client a 3-sentence interpretation.

## Files provided

- `examples.csv` — golden dataset (id, domain, label, golden_response)
- `model_outputs.csv` — model predictions (id, predicted_label, output)

## Deliverables

1. **Global metrics**: `needs_revision_precision`, `needs_revision_recall`,
   `accuracy`, `alignment_score`

2. **Per-domain breakdown**: same metrics split by the `domain` column.
   Flag any domain where accuracy < 0.80 as `underperforming: true`.

3. **False negatives**: Extract all examples where:
   - gold label = `needs_revision`
   - predicted label = `pass`
   These are the highest business risk (missed cases that needed review).

4. **Printed report**: JSON to stdout.

5. **Written interpretation**: 3 sentences max. What is the model doing well?
   Where is it failing? What is the single most important next step?

## Constraints

- Python only, stdlib + pandas allowed
- Do not hardcode any IDs
- Handle the case where golden_response is JSON (key-order invariant comparison)
- The pipeline must be runnable: `python solution.py`

## Evaluation criteria (what the interviewer is watching)

1. Do you read the brief before writing code?
2. Do you ask clarifying questions before making assumptions?
3. Is your confusion matrix correct (positive class = needs_revision)?
4. Do you handle JSON alignment correctly?
5. Is your code modular — reusable functions, not one giant block?
6. Do you communicate tradeoffs at the end?
