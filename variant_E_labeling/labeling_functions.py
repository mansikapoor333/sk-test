"""
Variant E — Write Labeling Functions + Quality Filter
=======================================================
Context: A client wants to classify customer support tickets.
         Rather than hand-labeling 50,000 tickets, you'll write
         labeling functions (LFs) that programmatically assign labels.

Positive class: ESCALATE  (ticket needs urgent human attention)
Negative class: RESOLVE   (ticket can be auto-resolved)
Abstain:        ABSTAIN   (-1) the LF is not confident, does not vote

RULES FOR LABELING FUNCTIONS:
  1. A LF returns ESCALATE, RESOLVE, or ABSTAIN
  2. ABSTAIN means "I don't know" — do NOT vote when unsure
  3. High precision with low coverage beats low precision with high coverage
  4. Multiple LFs are combined by a label model (not your job here)

YOUR TASKS:
  1. Implement 5 labeling functions (stubs provided)
  2. Implement coverage() — % of examples each LF votes on
  3. Implement conflict_rate() — fraction of examples where 2+ LFs disagree
  4. Implement quality_filter() — remove ambiguous synthetic examples

Run: python labeling_functions.py
"""

ABSTAIN  = -1
ESCALATE =  1
RESOLVE  =  0

TICKETS = [
    {"id": "1",  "text": "I want to cancel my subscription immediately.", "amount": 0},
    {"id": "2",  "text": "My bill shows $1,200 but I was quoted $400. Fix this or I'm calling my lawyer.", "amount": 1200},
    {"id": "3",  "text": "How do I reset my password?", "amount": 0},
    {"id": "4",  "text": "Great product, love it!", "amount": 0},
    {"id": "5",  "text": "I've been charged 3 times for the same order. This is fraud.", "amount": 0},
    {"id": "6",  "text": "Where is my order? It's been 6 weeks.", "amount": 0},
    {"id": "7",  "text": "I need a refund of $850 for a product that never arrived.", "amount": 850},
    {"id": "8",  "text": "Can you help me update my email address?", "amount": 0},
    {"id": "9",  "text": "UNACCEPTABLE service. I am contacting the BBB and filing a chargeback.", "amount": 0},
    {"id": "10", "text": "What are your business hours?", "amount": 0},
    {"id": "11", "text": "My account has been hacked. Someone made $2,300 in purchases.", "amount": 2300},
    {"id": "12", "text": "The checkout page isn't loading. Minor bug.", "amount": 0},
    {"id": "13", "text": "I demand a full refund. This is absolutely unacceptable.", "amount": 0},
    {"id": "14", "text": "Just checking on the status of my return.", "amount": 0},
    {"id": "15", "text": "I will be disputing this charge with my credit card company.", "amount": 0},
]

GOLD_LABELS = {
    "1": ESCALATE, "2": ESCALATE, "3": RESOLVE,  "4": RESOLVE,
    "5": ESCALATE, "6": ESCALATE, "7": ESCALATE, "8": RESOLVE,
    "9": ESCALATE, "10": RESOLVE, "11": ESCALATE, "12": RESOLVE,
    "13": ESCALATE, "14": RESOLVE, "15": ESCALATE,
}


# ─── TASK 1: IMPLEMENT THESE (stubs) ─────────────────────────────────────────

def lf_legal_threat(ticket):
    """ESCALATE if legal action keywords. ABSTAIN otherwise."""
    # TODO
    pass

def lf_large_billing_dispute(ticket):
    """ESCALATE if billing mention AND amount > 500. ABSTAIN otherwise."""
    # TODO
    pass

def lf_fraud_keywords(ticket):
    """ESCALATE if fraud/hacked/unauthorized/chargeback. ABSTAIN otherwise."""
    # TODO
    pass

def lf_simple_question(ticket):
    """RESOLVE if clearly a simple question, no negative sentiment. ABSTAIN otherwise."""
    # TODO
    pass

def lf_positive_sentiment(ticket):
    """RESOLVE if positive sentiment. ABSTAIN otherwise."""
    # TODO
    pass

def coverage(lf, tickets):
    """Fraction of tickets where lf does NOT return ABSTAIN."""
    # TODO
    pass

def conflict_rate(lfs, tickets):
    """Fraction of tickets where >=2 LFs disagree (one ESCALATE, one RESOLVE)."""
    # TODO
    pass

def quality_filter(synthetic_examples, lfs, min_coverage_votes=2):
    """Keep only examples where >=min_coverage_votes LFs agree with no conflicts."""
    # TODO
    pass


# ─── SOLUTIONS ────────────────────────────────────────────────────────────────

def lf_legal_threat_SOL(ticket):
    keywords = ["lawyer", "attorney", "sue", "lawsuit", "legal action",
                "court", "chargeback", "bbb", "dispute"]
    if any(k in ticket["text"].lower() for k in keywords):
        return ESCALATE
    return ABSTAIN

def lf_large_billing_dispute_SOL(ticket):
    text = ticket["text"].lower()
    billing = ["bill", "charge", "invoice", "payment", "refund", "fee"]
    if any(w in text for w in billing) and ticket.get("amount", 0) > 500:
        return ESCALATE
    return ABSTAIN

def lf_fraud_keywords_SOL(ticket):
    keywords = ["fraud", "hacked", "unauthorized", "stolen", "chargeback", "identity theft"]
    if any(k in ticket["text"].lower() for k in keywords):
        return ESCALATE
    return ABSTAIN

def lf_simple_question_SOL(ticket):
    text = ticket["text"].lower()
    negative = ["not", "never", "unacceptable", "horrible", "fraud",
                "charg", "refund", "cancel", "demand", "lawyer"]
    q_words  = ["how", "what", "where", "when", "can you", "could you", "help me"]
    has_q    = any(q in text for q in q_words) or text.endswith("?")
    has_neg  = any(n in text for n in negative)
    if has_q and not has_neg and len(text.split()) < 20:
        return RESOLVE
    return ABSTAIN

def lf_positive_sentiment_SOL(ticket):
    keywords = ["love", "great", "thank", "happy", "excellent", "good", "amazing"]
    if any(k in ticket["text"].lower() for k in keywords):
        return RESOLVE
    return ABSTAIN

def coverage_SOL(lf, tickets):
    votes = [lf(t) for t in tickets]
    return sum(1 for v in votes if v != ABSTAIN) / len(tickets)

def conflict_rate_SOL(lfs, tickets):
    conflicts = 0
    for t in tickets:
        votes = [lf(t) for lf in lfs if lf(t) != ABSTAIN]
        if ESCALATE in votes and RESOLVE in votes:
            conflicts += 1
    return conflicts / len(tickets)

def quality_filter_SOL(synthetic_examples, lfs, min_coverage_votes=2):
    kept, rejected = [], []
    for ex in synthetic_examples:
        votes = [lf(ex) for lf in lfs if lf(ex) != ABSTAIN]
        has_conflict = ESCALATE in votes and RESOLVE in votes
        if len(votes) >= min_coverage_votes and not has_conflict:
            kept.append(ex)
        else:
            rejected.append(ex)
    return kept, rejected


# ─── EVALUATION ───────────────────────────────────────────────────────────────

def evaluate_lfs(lfs):
    print("=== LF Coverage ===")
    for lf in lfs:
        cov = coverage_SOL(lf, TICKETS)
        print(f"  {lf.__name__:35s}: {cov:.0%}")

    print(f"\n=== Conflict Rate ===")
    cr = conflict_rate_SOL(lfs, TICKETS)
    print(f"  {cr:.0%} of examples have LF conflicts")

    print("\n=== LF Accuracy vs Gold Labels ===")
    for lf in lfs:
        votes = [(lf(t), GOLD_LABELS[t["id"]]) for t in TICKETS if lf(t) != ABSTAIN]
        if votes:
            correct = sum(1 for v, g in votes if v == g)
            print(f"  {lf.__name__:35s}: {correct}/{len(votes)} correct ({correct/len(votes):.0%} precision)")
        else:
            print(f"  {lf.__name__:35s}: abstained on everything")


if __name__ == "__main__":
    sol_lfs = [lf_legal_threat_SOL, lf_large_billing_dispute_SOL,
               lf_fraud_keywords_SOL, lf_simple_question_SOL,
               lf_positive_sentiment_SOL]
    evaluate_lfs(sol_lfs)
