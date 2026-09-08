# Interviewer Follow-Up Questions & Answers
# Every probe you'll face, with the answer to give

═══════════════════════════════════════════════════════════════
BLOCK 1 — CONFUSION MATRIX & METRICS
(Asked in all variants after you compute metrics)
═══════════════════════════════════════════════════════════════

Q: "Why did you choose precision/recall over accuracy as your headline metric?"
A: "Accuracy is misleading on imbalanced datasets. If 90% of examples are 'pass',
   a model that always predicts 'pass' gets 90% accuracy but catches zero
   needs_revision cases — recall is 0. Recall directly measures what the
   business cares about: of all the cases that actually needed review,
   how many did we catch? I report both, but I flag recall to the client
   because a missed case (false negative) typically has a higher business
   cost than a false alarm (false positive)."

Q: "When would you optimize for precision over recall?"
A: "When the cost of a false alarm is high. In a medical alert system,
   false alarms cause alert fatigue — doctors start ignoring the system.
   In a content moderation system, false alarms remove legitimate content
   and create a bad user experience. The right tradeoff depends on which
   failure mode is more expensive. I always ask the client: what costs you
   more — a missed case or a false alarm?"

Q: "What is F1 and when do you use it?"
A: "F1 is the harmonic mean of precision and recall: 2PR/(P+R).
   It gives a single number that balances both. I use it when the dataset
   is imbalanced and I want a single metric for model comparison or
   for a CI/CD gate. The harmonic mean punishes extreme values —
   a model with P=1.0 and R=0.1 gets F1=0.18, not 0.55.
   That's the right behavior: a model that never flags anything isn't useful
   even if it has perfect precision on the few things it does flag."

Q: "Your accuracy is 84% but the client says the model feels broken. Why?"
A: "Classic accuracy paradox on imbalanced classes. If 70% of examples are
   'pass', a model that always predicts 'pass' gets 70% accuracy but has
   0% recall on needs_revision. The model is 'broken' because it misses
   every case that actually matters. I'd immediately pull the per-class
   breakdown and show recall specifically on the positive class.
   That's the number that explains why the client feels this way."

Q: "What does a false negative mean in this context and why is it the highest risk?"
A: "A false negative is an example where the gold label is 'needs_revision'
   but the model predicted 'pass'. In a medical coding context, that's a
   claim that should have been reviewed by a human coder but wasn't —
   it gets submitted with a potentially wrong ICD code. That could mean
   a denied claim, an audit flag, or a compliance violation. In customer
   support, it's an escalation that needed a human but got auto-closed.
   False negatives are silent failures — the user never even knows they
   were missed."

═══════════════════════════════════════════════════════════════
BLOCK 2 — JSON ALIGNMENT & NORMALIZATION
(Asked whenever alignment_score comes up)
═══════════════════════════════════════════════════════════════

Q: "Why did you use json.loads instead of just strip().lower()?"
A: "Because two JSON strings can be semantically identical but textually
   different. {"a":1,"b":2} and {"b":2,"a":1} represent the same object.
   strip().lower() would say they're different. json.loads parses both
   into Python dicts, which compare by value not by string representation.
   I then re-serialize with sort_keys=True to get a canonical string for
   comparison. The try/except handles non-JSON responses by falling back
   to string comparison."

Q: "What's the tuple trick — why return ('json', ...) instead of just the string?"
A: "It prevents a JSON value from accidentally equaling a plain string.
   Suppose the golden_response is the JSON string '42' (a number) and the
   model output is the plain string '42'. Without the type tag:
     json.loads('42') = 42 -> json.dumps = '42' (same as the plain string)
   That would look aligned when it might not be. The tuple ('json', '42')
   can never equal ('str', '42'), so the type mismatch is preserved."

Q: "What if one side is valid JSON and the other isn't?"
A: "Not aligned — and that's the right answer. If the golden response is
   valid JSON but the model output fails to parse, the model is producing
   output in the wrong format. I'd flag that as an alignment failure,
   not a normalization edge case."

Q: "What if both are JSON but one is a nested object with string values
    that are themselves JSON?"
A: "That's a recursive normalization problem. My current solution handles
   one level — it parses the outer JSON and re-serializes it. If the values
   themselves are JSON strings, they'd be compared as strings. If I needed
   to handle this, I'd write a recursive normalize that tries json.loads
   on every string value. But I'd only add that complexity if I confirmed
   this case exists in the actual data."

═══════════════════════════════════════════════════════════════
BLOCK 3 — CODE QUALITY & DESIGN
(Asked in all variants)
═══════════════════════════════════════════════════════════════

Q: "Why did you build lookup dicts instead of using zip or nested loops?"
A: "Because I can't assume the lists are in the same order. examples and
   model_outputs might be sorted differently, have different lengths if
   something failed, or be loaded from separate database queries. Building
   gold = {e['id']: e for e in examples} and then iterating over gold keys
   guarantees I'm comparing the right pairs. If an ID is missing in either
   list, I get a KeyError immediately — that's better than silently comparing
   wrong examples."

Q: "What happens if an ID is in model_outputs but not in examples?"
A: "With my current implementation, nothing — I iterate over examples and
   look up in model_outputs, so extra IDs in outputs are silently ignored.
   In production I'd add a validation step: assert that the sets of IDs match
   exactly before running any metrics. A mismatch usually means a data pipeline
   issue that should be surfaced, not silently swallowed."

Q: "Why did you separate build_confusion_matrix() from the metric functions?"
A: "Because I compute the confusion matrix four times — once per metric.
   If I inline it in each function, I call it redundantly and the code
   becomes hard to test. By extracting it, I can test the confusion matrix
   independently, and the metric functions become one-liners. It also makes
   the code easier to read: the structure mirrors the math."

Q: "How would you make this pipeline handle 10 million examples efficiently?"
A: "Three changes: (1) don't load everything into memory at once — use
   streaming/batching. (2) Replace the Python loop with vectorized pandas
   operations or a SQL GROUP BY query. (3) For the JSON normalization,
   cache the normalized form so we don't re-parse the same golden_response
   multiple times if it appears across examples. At 10M rows I'd probably
   run this in Spark or push the confusion matrix computation into SQL."

═══════════════════════════════════════════════════════════════
BLOCK 4 — SQL SPECIFIC
(Asked in Variant D or if interviewer pivots to data analysis)
═══════════════════════════════════════════════════════════════

Q: "Why did you use 1.0 instead of 1 in your CASE WHEN?"
A: "Integer division. In SQLite and most SQL dialects, 6/8 = 0, not 0.75.
   Using 1.0 forces the SUM to be a float, so 6.0/8 = 0.75.
   Alternatively you can cast: CAST(SUM(...) AS FLOAT). Either works,
   but the 1.0 trick is more concise."

Q: "What's the difference between WHERE and HAVING?"
A: "WHERE filters rows before grouping — it operates on individual row values.
   HAVING filters groups after GROUP BY — it operates on aggregate values like
   SUM or COUNT. So 'WHERE domain = cardiology' keeps only cardiology rows
   before aggregating. 'HAVING COUNT(*) > 5' keeps only groups with more
   than 5 rows, evaluated after the GROUP BY runs."

Q: "How would you make the domain accuracy query faster on 100M rows?"
A: "Add a composite index on (domain, label, predicted_label) so the
   database can compute the GROUP BY and CASE WHEN from the index alone
   without scanning the full table. This is a covering index — all the
   columns the query needs are in the index. On 100M rows this could be
   a 10x speedup over a full table scan."

Q: "NULLIF(TP + FP, 0) — what does that do?"
A: "NULLIF(x, 0) returns NULL if x = 0, otherwise returns x. This prevents
   divide-by-zero errors. In SQL, any arithmetic with NULL returns NULL,
   so TP / NULLIF(TP+FP, 0) returns NULL instead of crashing when the
   denominator is 0. I then handle NULL in the output layer — either with
   COALESCE(result, 0.0) or by displaying it as 'N/A'."

═══════════════════════════════════════════════════════════════
BLOCK 5 — LABELING FUNCTIONS
(Asked in Variant E or if interviewer asks about Snorkel's approach)
═══════════════════════════════════════════════════════════════

Q: "Why does an LF return ABSTAIN instead of just guessing?"
A: "Because a wrong vote is worse than no vote. The label model combines
   LF outputs by weighting them based on their accuracy. An LF that
   abstains on uncertain cases has higher precision on the examples it
   does vote on — that precision is what the label model uses to determine
   how much to trust it. An LF that always votes, even when uncertain,
   dilutes its signal and lowers its learned accuracy weight."

Q: "Your LF has 100% precision but only 5% coverage. Is that good?"
A: "Yes, if you have other LFs covering the remaining 95%. A high-precision
   LF that fires rarely is the most trustworthy input to the label model.
   The problem arises if ALL your LFs have low coverage — then most examples
   have no votes and get no label. You want a portfolio: a few high-precision
   narrow LFs plus a few broader LFs with lower (but acceptable) precision
   to ensure coverage. The label model handles the noise from the broader LFs."

Q: "Two LFs vote ESCALATE and one votes RESOLVE on the same example.
    What does the label model do?"
A: "It doesn't just take a majority vote. It weights each LF's vote by
   its learned accuracy, which it estimates from the LFs' agreement and
   disagreement patterns across the unlabeled data. If the two ESCALATE
   LFs are more accurate (higher estimated precision from historical patterns),
   the label model up-weights them. If the RESOLVE LF is historically
   more accurate, it might override. The output is a probability distribution
   over labels, not a hard vote — for example: P(ESCALATE) = 0.82."

Q: "When would you NOT use labeling functions?"
A: "When the task can't be expressed as rules. If the label requires
   subjective judgment — 'is this response empathetic?' — no keyword
   or regex can capture it. Also when the label space is ambiguous and
   SMEs themselves disagree on the schema. And when you already have
   200+ clean labeled examples and a simple task — at that point,
   just fine-tune directly, the overhead of writing LFs isn't worth it."

═══════════════════════════════════════════════════════════════
BLOCK 6 — LLM JUDGE
(Asked in Variant F or as a follow-up to alignment_score)
═══════════════════════════════════════════════════════════════

Q: "Your judge prompt asks for 'aligned' or 'not_aligned'. What if it
    returns 'yes' or 'partially aligned'?"
A: "I treat anything that isn't exactly 'aligned' as 'not_aligned' —
   safe default. I also log the unexpected response so I can debug
   the prompt. The fix for partial or unexpected responses is to
   make the prompt more constrained: 'Respond with EXACTLY the word
   aligned or not_aligned. Nothing else. No punctuation.' And add
   an example of each in the prompt so the model has a pattern to follow."

Q: "LLM judges are non-deterministic. How do you get reproducible scores?"
A: "temperature=0 is the first line of defense. For models where temperature
   can't be zeroed, I run N=5 judgments and take the majority vote, and I
   report variance as a confidence interval. I also pin the model version —
   'gpt-4o-2024-05-13' not 'gpt-4o-latest' — because model updates change
   behavior. Everything is logged: prompt version, model version, timestamp,
   raw output. That way I can reproduce any individual judgment."

Q: "When would you use exact-match instead of an LLM judge?"
A: "When the output is structured and canonical — ICD codes, JSON with a
   defined schema, classification labels, numeric results. Exact match is
   free, deterministic, and doesn't hallucinate. I only reach for an LLM
   judge when the output is free-form text where paraphrases should count
   as correct, or when the definition of 'correct' requires understanding
   semantic meaning, not just surface form."

Q: "What's your biggest concern about using an LLM as a judge?"
A: "Reward hacking and bias amplification. If the judge has a systematic
   preference — verbose responses, formal language, a particular answer
   format — a model trained to score well on this judge will learn to
   satisfy the judge prompt rather than the underlying task. I mitigate
   this by calibrating the judge against human labels on 50–100 examples
   before using it at scale. If judge-human agreement (Cohen's kappa) is
   below 0.6, the judge isn't reliable enough and I need to revise the prompt."

═══════════════════════════════════════════════════════════════
BLOCK 7 — "WHAT WOULD YOU DO NEXT?" (closing question)
═══════════════════════════════════════════════════════════════

The interviewer will always end with a version of this. Have an answer ready.

Q: "If you had 30 more minutes, what would you add?"
A: "Three things in priority order:
   First, per-domain breakdown — global metrics hide domain-specific failures.
   A model might have 90% recall in finance but 40% recall in medical. The
   client needs to know that before deploying.
   
   Second, false negative inspection — I'd extract the FN examples and look
   for patterns. If all missed cases share a domain, a text length, or a
   specific response format, that tells me exactly what data to add to fix it.
   
   Third, if eval libraries are available, I'd add sklearn's
   classification_report to get per-class metrics in one call, and
   use pandas for the domain breakdown groupby — cleaner than a defaultdict
   loop for a real deliverable."

Q: "How would you present these results to a non-technical stakeholder?"
A: "Three sentences max:
   'The model correctly identifies [X]% of cases overall. However, it misses
   1 in [N] cases that actually needed review — those are the highest risk.
   The [domain] category has the highest miss rate and should be prioritized
   for additional training data.'
   
   Then one concrete example of a false negative — a real case the model missed
   — to make the risk tangible. Numbers plus a story is more persuasive than
   numbers alone."
