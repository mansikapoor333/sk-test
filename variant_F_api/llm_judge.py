"""
Variant F — LLM-as-a-Judge API Integration
============================================
Context: Exact-match alignment misses semantically correct answers.
         You'll build an LLM judge that evaluates model outputs
         against golden responses using an API call.

This is the most realistic version of what Snorkel's FDE team
actually builds in production.

YOUR TASKS:
  1. Implement build_judge_prompt() — design a prompt that
     returns exactly "aligned" or "not_aligned"
  2. Implement call_judge() — call the API, parse response,
     handle errors gracefully
  3. Implement llm_alignment_score() — run the judge on all
     examples, return the score
  4. Implement compare_scores() — compare exact-match vs LLM judge
     and report the delta per domain

The API is stubbed — replace the stub with a real call during the
interview if the interviewer provides an API key.

Run: python llm_judge.py
"""

import json
import time
from collections import defaultdict

# ─── DATA ────────────────────────────────────────────────────────────────────

EXAMPLES = [
    {"id": "1",  "domain": "medical",  "task": "Code this: Hypertension",
     "golden_response": "ICD-10: I10 — Essential hypertension"},
    {"id": "2",  "domain": "medical",  "task": "Code this: Type 2 diabetes without complications",
     "golden_response": "ICD-10: E11.9 — Type 2 diabetes mellitus without complications"},
    {"id": "3",  "domain": "legal",    "task": "Is this clause enforceable: 'All disputes settled by arbitration in Delaware.'",
     "golden_response": "Yes, arbitration clauses are generally enforceable under the Federal Arbitration Act."},
    {"id": "4",  "domain": "legal",    "task": "Is this clause enforceable: 'Employee waives all overtime rights.'",
     "golden_response": "No, FLSA overtime rights cannot be waived by private agreement."},
    {"id": "5",  "domain": "finance",  "task": "Classify this transaction risk: wire transfer $45K, new vendor, no PO",
     "golden_response": "High risk — missing purchase order and unverified vendor."},
    {"id": "6",  "domain": "finance",  "task": "Classify this transaction risk: monthly payroll $230K, all verified",
     "golden_response": "Low risk — routine payroll with verified employees."},
]

# Model outputs — some are exact matches, some are paraphrases, some are wrong
MODEL_OUTPUTS = [
    {"id": "1",  "output": "Essential (primary) hypertension, ICD10 code I10"},       # paraphrase → LLM judge catches, exact misses
    {"id": "2",  "output": "ICD-10: E11.9 — Type 2 diabetes mellitus without complications"},  # exact match
    {"id": "3",  "output": "Generally yes, such clauses are enforceable per the FAA."},         # paraphrase
    {"id": "4",  "output": "This clause is not enforceable under FLSA regulations."},           # paraphrase
    {"id": "5",  "output": "Low risk."},                                               # WRONG
    {"id": "6",  "output": "Low risk — routine payroll with verified employees."},     # exact match
]


# ─── TASK 1: JUDGE PROMPT ────────────────────────────────────────────────────

def build_judge_prompt(task, golden_response, model_output):
    """
    Build a prompt that instructs the LLM judge to return exactly:
      "aligned"     — if model_output is semantically correct
      "not_aligned" — if model_output is wrong, incomplete, or misleading

    Good prompt design:
      - Clear role definition
      - Explicit rubric (what counts as aligned vs not)
      - Show an example of aligned and not_aligned
      - Demand exactly one word output: "aligned" or "not_aligned"
      - No explanation, no other text

    Bad prompt: "Is this correct? Yes or No."
    (Too vague. The judge won't know what criteria to use.)
    """
    # TODO — write the prompt string
    pass


# ─── TASK 2: API CALL ────────────────────────────────────────────────────────

def call_judge(prompt, model="claude-sonnet-4-6", max_retries=3):
    """
    Call the LLM judge API and return "aligned" or "not_aligned".

    Error handling requirements:
      - If the API returns something other than "aligned"/"not_aligned":
        log it and return "not_aligned" (safe default)
      - If the API call fails (network error, rate limit):
        retry up to max_retries times with exponential backoff
      - If all retries fail: return "not_aligned"

    For the interview: the stub below always returns "aligned".
    Replace with a real API call if an API key is provided.
    """
    # STUB — replace with real call:
    # import anthropic
    # client = anthropic.Anthropic()
    # message = client.messages.create(
    #     model=model,
    #     max_tokens=10,
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return message.content[0].text.strip().lower()

    # Simulate: return "aligned" for most, "not_aligned" for id "5"
    if "Low risk." in prompt and "High risk" in prompt:
        return "not_aligned"
    return "aligned"


# ─── TASK 3: LLM ALIGNMENT SCORE ─────────────────────────────────────────────

def llm_alignment_score(examples, model_outputs):
    """
    For each example, build the judge prompt and call the judge.
    Return:
      {
        "llm_alignment_score": float,
        "per_example": [{"id": ..., "judgment": "aligned"/"not_aligned"}, ...]
      }

    Important: build a lookup dict by ID first. Don't assume the lists
    are in the same order.
    """
    # TODO
    pass


# ─── TASK 4: COMPARE EXACT VS LLM ────────────────────────────────────────────

def exact_match_score(examples, model_outputs):
    """
    Compute exact-match alignment score (no LLM, just string/JSON comparison).
    Reuse your normalize() and is_aligned() logic from the other variants.
    """
    def normalize(r):
        try:
            return ("json", json.dumps(json.loads(r), sort_keys=True))
        except Exception:
            return ("str", r.strip().lower())

    gold   = {e["id"]: e["golden_response"] for e in examples}
    output = {o["id"]: o["output"] for o in model_outputs}
    aligned = sum(1 for id_ in gold if normalize(output[id_]) == normalize(gold[id_]))
    return round(aligned / len(gold), 4)


def compare_scores(examples, model_outputs):
    """
    Compare exact-match vs LLM judge alignment score.
    Return:
      {
        "exact_match":  float,
        "llm_judge":    float,
        "delta":        float,   # llm - exact (positive = LLM is more generous)
        "cases_llm_catches_exact_misses": [list of ids]  # paraphrases
      }
    """
    # TODO
    pass


# ─── SOLUTIONS (reveal after attempting) ─────────────────────────────────────

def build_judge_prompt_SOL(task, golden_response, model_output):
    return f"""You are an expert evaluator assessing whether a model's answer is correct.

Task given to the model: {task}

Correct answer (golden response): {golden_response}

Model's answer: {model_output}

Evaluation criteria:
- "aligned": The model's answer conveys the same meaning as the correct answer,
  even if worded differently. Minor paraphrasing is acceptable.
- "not_aligned": The model's answer is factually wrong, incomplete in a material
  way, or contradicts the correct answer.

Examples:
- Golden: "ICD-10: I10 — Essential hypertension"
  Model:  "Essential hypertension, code I10"
  Verdict: aligned (same meaning, different format)

- Golden: "High risk — missing purchase order"
  Model:  "Low risk"
  Verdict: not_aligned (contradicts the correct answer)

Respond with EXACTLY one word: aligned or not_aligned
No explanation. No punctuation. No other text."""


def llm_alignment_score_SOL(examples, model_outputs):
    gold_map   = {e["id"]: e for e in examples}
    output_map = {o["id"]: o for o in model_outputs}
    per_example = []
    aligned_count = 0
    for ex in examples:
        id_     = ex["id"]
        task    = ex.get("task", "")
        golden  = ex["golden_response"]
        output  = output_map[id_]["output"]
        prompt  = build_judge_prompt_SOL(task, golden, output)
        verdict = call_judge(prompt)
        per_example.append({"id": id_, "judgment": verdict})
        if verdict == "aligned":
            aligned_count += 1
    return {
        "llm_alignment_score": round(aligned_count / len(examples), 4),
        "per_example": per_example,
    }


def compare_scores_SOL(examples, model_outputs):
    exact = exact_match_score(examples, model_outputs)
    llm   = llm_alignment_score_SOL(examples, model_outputs)
    llm_score = llm["llm_alignment_score"]

    # Find cases LLM catches that exact-match misses
    def normalize(r):
        try: return ("json", json.dumps(json.loads(r), sort_keys=True))
        except: return ("str", r.strip().lower())

    gold_map   = {e["id"]: e["golden_response"] for e in examples}
    output_map = {o["id"]: o["output"] for o in model_outputs}
    exact_miss = {e["id"] for e in examples
                  if normalize(output_map[e["id"]]) != normalize(gold_map[e["id"]])}
    llm_caught = {r["id"] for r in llm["per_example"]
                  if r["judgment"] == "aligned" and r["id"] in exact_miss}

    return {
        "exact_match":  exact,
        "llm_judge":    llm_score,
        "delta":        round(llm_score - exact, 4),
        "cases_llm_catches_exact_misses": list(llm_caught),
    }


def main():
    print("=== Exact Match Score ===")
    print(f"  {exact_match_score(EXAMPLES, MODEL_OUTPUTS):.0%}")

    print("\n=== LLM Judge Score ===")
    result = llm_alignment_score_SOL(EXAMPLES, MODEL_OUTPUTS)
    print(f"  {result['llm_alignment_score']:.0%}")
    for r in result["per_example"]:
        print(f"    {r['id']}: {r['judgment']}")

    print("\n=== Comparison ===")
    comp = compare_scores_SOL(EXAMPLES, MODEL_OUTPUTS)
    print(json.dumps(comp, indent=2))

    print("\n=== Sample Judge Prompt (id=1) ===")
    ex = EXAMPLES[0]
    out = MODEL_OUTPUTS[0]
    print(build_judge_prompt_SOL(ex["task"], ex["golden_response"], out["output"]))


if __name__ == "__main__":
    main()
