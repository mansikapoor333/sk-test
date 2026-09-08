-- ═══════════════════════════════════════════════════════════════
-- Variant D — SQL Data Analysis
-- ═══════════════════════════════════════════════════════════════
-- Schema: an eval pipeline stores results in a relational DB.
-- Your job: write queries to answer the 6 questions below.
-- Database: SQLite (standard SQL, no window functions required
--           but you may use them if you know them)
-- ═══════════════════════════════════════════════════════════════

-- ── SCHEMA ───────────────────────────────────────────────────────

CREATE TABLE examples (
    id              TEXT PRIMARY KEY,
    domain          TEXT NOT NULL,          -- e.g. 'cardiology', 'oncology'
    label           TEXT NOT NULL,          -- 'pass' or 'needs_revision'
    golden_response TEXT NOT NULL
);

CREATE TABLE model_outputs (
    id               TEXT PRIMARY KEY,
    predicted_label  TEXT NOT NULL,         -- 'pass' or 'needs_revision'
    output           TEXT NOT NULL,
    model_version    TEXT NOT NULL,         -- e.g. 'gpt-4o-2024-05', 'claude-3-5'
    run_timestamp    TEXT NOT NULL          -- ISO 8601 e.g. '2025-03-15T09:00:00'
);

-- ── QUESTION 1 ───────────────────────────────────────────────────
-- Count TP, FP, FN, TN across the entire dataset.
-- Positive class = 'needs_revision'.
-- Columns: TP, FP, FN, TN

-- YOUR ANSWER:


-- SOLUTION:
SELECT
    SUM(CASE WHEN e.label = 'needs_revision' AND o.predicted_label = 'needs_revision' THEN 1 ELSE 0 END) AS TP,
    SUM(CASE WHEN e.label = 'pass'           AND o.predicted_label = 'needs_revision' THEN 1 ELSE 0 END) AS FP,
    SUM(CASE WHEN e.label = 'needs_revision' AND o.predicted_label = 'pass'           THEN 1 ELSE 0 END) AS FN,
    SUM(CASE WHEN e.label = 'pass'           AND o.predicted_label = 'pass'           THEN 1 ELSE 0 END) AS TN
FROM examples e
JOIN model_outputs o ON e.id = o.id;

-- ── QUESTION 2 ───────────────────────────────────────────────────
-- Compute precision, recall, and accuracy for the entire dataset.
-- Columns: precision, recall, accuracy
-- Tip: use the TP/FP/FN/TN you computed above as a subquery or CTE.

-- YOUR ANSWER:


-- SOLUTION:
WITH cm AS (
    SELECT
        SUM(CASE WHEN e.label = 'needs_revision' AND o.predicted_label = 'needs_revision' THEN 1.0 ELSE 0 END) AS TP,
        SUM(CASE WHEN e.label = 'pass'           AND o.predicted_label = 'needs_revision' THEN 1.0 ELSE 0 END) AS FP,
        SUM(CASE WHEN e.label = 'needs_revision' AND o.predicted_label = 'pass'           THEN 1.0 ELSE 0 END) AS FN,
        SUM(CASE WHEN e.label = 'pass'           AND o.predicted_label = 'pass'           THEN 1.0 ELSE 0 END) AS TN,
        COUNT(*) AS total
    FROM examples e
    JOIN model_outputs o ON e.id = o.id
)
SELECT
    ROUND(TP / NULLIF(TP + FP, 0), 4) AS precision,
    ROUND(TP / NULLIF(TP + FN, 0), 4) AS recall,
    ROUND((TP + TN) / total,        4) AS accuracy
FROM cm;

-- ── QUESTION 3 ───────────────────────────────────────────────────
-- Compute accuracy per domain. Order by accuracy ascending
-- so the worst-performing domain appears first.
-- Columns: domain, accuracy, total_examples

-- YOUR ANSWER:


-- SOLUTION:
SELECT
    e.domain,
    ROUND(
        SUM(CASE WHEN e.label = o.predicted_label THEN 1.0 ELSE 0 END) / COUNT(*),
    4) AS accuracy,
    COUNT(*) AS total_examples
FROM examples e
JOIN model_outputs o ON e.id = o.id
GROUP BY e.domain
ORDER BY accuracy ASC;

-- ── QUESTION 4 ───────────────────────────────────────────────────
-- List all false negatives: gold=needs_revision, predicted=pass.
-- These are the highest business risk (missed cases).
-- Columns: id, domain, golden_response
-- Order by domain.

-- YOUR ANSWER:


-- SOLUTION:
SELECT
    e.id,
    e.domain,
    e.golden_response
FROM examples e
JOIN model_outputs o ON e.id = o.id
WHERE e.label          = 'needs_revision'
  AND o.predicted_label = 'pass'
ORDER BY e.domain;

-- ── QUESTION 5 ───────────────────────────────────────────────────
-- The model has been run in multiple versions (model_version column).
-- For each model version, compute recall on the needs_revision class.
-- Show which version has the best recall.
-- Columns: model_version, recall, rank (1 = best)

-- YOUR ANSWER:


-- SOLUTION:
WITH version_recall AS (
    SELECT
        o.model_version,
        SUM(CASE WHEN e.label = 'needs_revision' AND o.predicted_label = 'needs_revision' THEN 1.0 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN e.label = 'needs_revision' THEN 1.0 ELSE 0 END), 0)
            AS recall
    FROM examples e
    JOIN model_outputs o ON e.id = o.id
    GROUP BY o.model_version
)
SELECT
    model_version,
    ROUND(recall, 4) AS recall,
    RANK() OVER (ORDER BY recall DESC) AS rank
FROM version_recall
ORDER BY rank;

-- ── QUESTION 6 ───────────────────────────────────────────────────
-- Find domains where the false negative RATE exceeds 20%.
-- False negative rate = FN / (FN + TP) = missed / total actual positives.
-- Columns: domain, fn_rate, actual_positives
-- Order by fn_rate descending.
-- (This is the query a client would use to find where the model is most dangerous)

-- YOUR ANSWER:


-- SOLUTION:
SELECT
    e.domain,
    ROUND(
        SUM(CASE WHEN e.label = 'needs_revision' AND o.predicted_label = 'pass' THEN 1.0 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN e.label = 'needs_revision' THEN 1.0 ELSE 0 END), 0),
    4) AS fn_rate,
    SUM(CASE WHEN e.label = 'needs_revision' THEN 1 ELSE 0 END) AS actual_positives
FROM examples e
JOIN model_outputs o ON e.id = o.id
GROUP BY e.domain
HAVING fn_rate > 0.20
ORDER BY fn_rate DESC;


-- ═══════════════════════════════════════════════════════════════
-- WHAT THE INTERVIEWER IS WATCHING IN THE SQL ROUND
-- ═══════════════════════════════════════════════════════════════
--
-- 1. Do you write the JOIN correctly (e.id = o.id)?
-- 2. Do you use CASE WHEN ... THEN 1.0 ELSE 0 END for conditional sums?
--    (The 1.0 forces float division. 1 gives integer division in SQLite.)
-- 3. Do you handle divide-by-zero? (NULLIF(denom, 0) returns NULL
--    instead of crashing when denominator is 0)
-- 4. Do you use CTEs to avoid repeating the confusion matrix logic?
-- 5. Do you ROUND your metric columns (avoid 0.666666666 in output)?
-- 6. Can you write HAVING vs WHERE correctly?
--    (WHERE filters rows before grouping, HAVING filters after)
--
-- FOLLOW-UP QUESTIONS TO EXPECT:
-- "Why did you use 1.0 instead of 1 in the CASE WHEN?"
-- "What happens if a domain has 0 needs_revision examples?"
-- "How would you add a filter to show only runs from the last 30 days?"
-- "How would you rewrite Q5 without a window function?"
-- "What index would you add to make Q3 faster on 10M rows?"
