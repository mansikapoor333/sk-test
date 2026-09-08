# Snorkel AI — Senior FDE Technical Interview Simulator
# One Round. Everything you need to be ready for any variant.

═══════════════════════════════════════════════════════════════════
WHAT THE RECRUITER SAID
═══════════════════════════════════════════════════════════════════
"Build a custom evaluator and analyze the results. It will contain
a client brief, structured CSV, golden dataset, and a set of outputs
to evaluate against. You can import eval libraries and run them
and inspect findings."

WHAT 1POINT3ACRES CONFIRMED
═══════════════════════════════════════════════════════════════════
- CoderPad, 60 minutes
- 3 Python files given: examples.json, exercise.py, test_exercise.py
- Could be debugging (fix bugs so tests pass) OR build from scratch
- 1-word / 1-2 line fixes only if debugging
- Collaborative — you drive, interviewer asks questions
- Read before you code. Narrate your reasoning.
- Tests are always correct. Never modify tests.

WHAT THE JD ADDS
═══════════════════════════════════════════════════════════════════
- Python AND SQL explicitly required
- LLM/ML validation workflows
- API integrations
- Translating ambiguous requirements into specs
- Building quality measurement systems

═══════════════════════════════════════════════════════════════════
THE 6 QUESTION VARIANTS (any one could show up)
═══════════════════════════════════════════════════════════════════

Variant A — DEBUGGING (most likely based on 1point3acres)
  Files: variant_A_debugging/
  Task:  Fix 3 bugs in exercise.py so test_exercise.py passes
  Time:  60 min | Difficulty: Medium

Variant B — BUILD FROM SCRATCH (what recruiter described)
  Files: variant_B_build/
  Task:  Implement blank functions using client brief + CSVs
  Time:  60 min | Difficulty: Medium-Hard

Variant C — EXTEND AN EXISTING PIPELINE
  Files: variant_C_extend/
  Task:  Add per-domain breakdown + LLM judge to working code
  Time:  60 min | Difficulty: Medium

Variant D — SQL DATA ANALYSIS
  Files: variant_D_sql/
  Task:  Write SQL queries to analyze eval results in a database
  Time:  30-45 min | Difficulty: Medium

Variant E — SYNTHETIC DATA + LABELING FUNCTIONS
  Files: variant_E_labeling/
  Task:  Write labeling functions + quality filter for synthetic data
  Time:  60 min | Difficulty: Medium-Hard

Variant F — API INTEGRATION
  Files: variant_F_api/
  Task:  Call an LLM API as a judge, handle errors, compute metrics
  Time:  60 min | Difficulty: Medium-Hard

═══════════════════════════════════════════════════════════════════
THE ONE MENTAL MODEL THAT UNLOCKS EVERY VARIANT
═══════════════════════════════════════════════════════════════════

Every question is the same core loop:

  1. Load examples (gold labels + golden responses)
  2. Load model outputs (predicted labels + outputs)
  3. Build a lookup: gold dict + pred dict keyed by id
  4. Iterate over IDs, apply a comparison
  5. Compute metrics from TP/FP/FN/TN
  6. Normalize JSON outputs before comparing (sort_keys)
  7. Report + interpret

Once you internalize this loop, you just swap out step 4.

═══════════════════════════════════════════════════════════════════
CONFUSION MATRIX — MEMORIZE THIS
═══════════════════════════════════════════════════════════════════

Positive class = "needs_revision" (the thing you want to catch)

              Pred: needs_revision   Pred: pass
Gold: NR            TP                  FN      ← missed (HIGHEST RISK)
Gold: pass          FP                  TN      ← false alarm

Precision = TP / (TP + FP)    → of all flagged, how many were real
Recall    = TP / (TP + FN)    → of all real, how many did we catch
Accuracy  = (TP + TN) / total → fraction correct overall
F1        = 2PR / (P + R)     → harmonic mean (use on imbalanced data)

ALIGNMENT:
  If both parse as JSON → compare json.loads() structures (key-order invariant)
  Otherwise            → compare strip().lower() strings
  If one parses, other doesn't → NOT aligned

═══════════════════════════════════════════════════════════════════
INTERVIEW PROCESS — WHAT TO DO IN THE ROOM
═══════════════════════════════════════════════════════════════════

FIRST 10-15 MINUTES (do not write code):
  1. Read every file given to you. All of them.
  2. Read the docstrings and instruction blocks in exercise.py.
  3. Trace ONE example manually through the pipeline.
  4. State out loud: "Positive class is X. TP means Y. I'm going to
     start by understanding what each test expects before touching code."

IF DEBUGGING:
  - Run the tests first: python test_exercise.py
  - Read the failure message carefully — it usually names the bug
  - Never change the tests. Never change the thresholds.
  - Every fix is 1 word or 1-2 lines. Big rewrites = wrong direction.
  - Say: "The test expects X. The current code returns Y. The bug is Z."

IF BUILDING:
  - Ask ONE clarifying question before coding: "What is the positive class?"
  - Build modular functions — don't write everything in main()
  - Implement normalize() and is_aligned() FIRST (most bug-prone)
  - Test with a simple 2-example case mentally before running

ALWAYS SAY OUT LOUD:
  - "I'm going to normalize JSON through json.loads to handle key ordering"
  - "The thresholds in the tests are fixed spec — the bugs are in the code"
  - "False negatives are the highest business risk here — missed cases"
  - At the end: "If I had more time, I'd add per-domain breakdown and..."

═══════════════════════════════════════════════════════════════════
FOLLOW-UP QUESTIONS THE INTERVIEWER WILL ASK (with answers)
═══════════════════════════════════════════════════════════════════
See: interviewer_followups.md

═══════════════════════════════════════════════════════════════════
FILE MAP
═══════════════════════════════════════════════════════════════════
README.md                     ← you are here
interviewer_followups.md      ← every probe question + answer

variant_A_debugging/
  examples.json               ← golden dataset (16 examples, 5 domains)
  exercise.py                 ← BUGGY pipeline (3 bugs to find)
  test_exercise.py            ← DO NOT MODIFY (tests are correct)
  exercise_SOLUTION.py        ← answer key
  HINTS.md                    ← step-by-step hint progression

variant_B_build/
  client_brief.md             ← read this first
  examples.csv                ← 50 examples, 5 domains
  model_outputs.csv           ← 50 model predictions
  starter.py                  ← blank template to implement
  solution.py                 ← full answer key

variant_C_extend/
  working_pipeline.py         ← correct baseline (no bugs)
  extension_tasks.md          ← 3 features to add
  solution_extended.py        ← answer key

variant_D_sql/
  schema.sql                  ← database schema
  questions.md                ← 6 SQL questions
  solutions.sql               ← answer key

variant_E_labeling/
  brief.md                    ← labeling function task
  data_sample.json            ← sample data to label
  starter.py                  ← blank template
  solution.py                 ← answer key

variant_F_api/
  brief.md                    ← LLM-as-judge task
  examples.json               ← eval dataset
  starter.py                  ← blank template with stub
  solution.py                 ← answer key
