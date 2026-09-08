#Summary: 
Create an extensible library that processes return requests to determine the immediate refund amount and whether to AUTO_REFUND or send to MANUAL_REVIEW, designed to evolve as requirements grow.

# Returns Desk Refund System

# Problem Statement

Shopify operates a Returns Desk tool that helps support staff decide whether an order should be auto-refunded or routed for manual review.

Each "return request" event represents a buyer asking for a refund on an order.

Your job is to implement a small library that processes return requests and provides a decision for each request:

1. The refund amount that should be issued right now (may be `0.00`)
2. The decision (`"AUTO_REFUND"` or `"MANUAL_REVIEW"`)

We'll start with a simplified system and gradually add requirements. Try to design your code so it can be extended and refactored as the requirements evolve.

---

## Input Format

Each return request is a tuple:

```python
(request_id, order_id, buyer_email, shipping_address_id, payment_fingerprint, order_total, reason)
```

| Field | Description |
|-------|-------------|
| `request_id` | Unique identifier |
| `order_id` | Unique for this exercise |
| `buyer_email` | A string (may differ by casing/whitespace) |
| `shipping_address_id` | A string (already normalized) |
| `payment_fingerprint` | A tokenized string (already normalized) |
| `order_total` | A decimal number |
| `reason` | An enum string: `"DAMAGED"`, `"NOT_RECEIVED"`, `"CHANGED_MIND"` |

Your program will receive a list of return requests and must output, for each request:

```python
(request_id, refund_amount, decision)
```

---

## Stage 1 — Basic Refund Rule (Single-Request Logic)

For now, every request is evaluated independently.

### Policy

- If `reason == "DAMAGED"`: auto-refund the full `order_total`
- Otherwise: do not refund automatically; route to manual review

### Sample Input

```python
requests = [
  ("r1", "o100", "Alice@Example.com ", "addr_1", "card_A", 120.00, "DAMAGED"),
  ("r2", "o101", "bob@example.com",    "addr_2", "card_B",  80.00, "CHANGED_MIND"),
  ("r3", "o102", "cathy@example.com",  "addr_3", "card_C",  35.50, "DAMAGED"),
]
```

### Expected Output

```python
[
  ("r1", 120.00, "AUTO_REFUND"),
  ("r2",   0.00, "MANUAL_REVIEW"),
  ("r3",  35.50, "AUTO_REFUND"),
]
```

---

## Stage 2 — Email Normalization + Per-Buyer Daily Cap

We now want to limit accidental abuse and reduce operational risk.

### Policy

- Minor changes (casing, whitespaces, dots, etc.) are considered the same email
- A buyer can receive at most **$200** of auto-refunds per day (across all their requests)
- Once the cap is reached, we refund as much as we can and trigger a `"MANUAL_REVIEW"`
- Additional eligible refunds have `refund_amount = 0.00`

> **Note:** Assume all sample data is from the same day.

### Sample Input

```python
requests = [
  ("r1", "o200", "Alice@Example.com ", "addr_1", "card_A", 120.00, "DAMAGED"),
  ("r2", "o201", "alice@example.com",  "addr_4", "card_D",  90.00, "DAMAGED"),
  ("r3", "o202", "alice@example.com",  "addr_5", "card_E",  50.00, "DAMAGED"),
]
```

### Expected Output (cap is $200)

```python
[
  ("r1", 120.00, "AUTO_REFUND"),      # total auto-refunds for alice: 120
  ("r2",  80.00, "MANUAL_REVIEW"),    # only 80 left before hitting cap (200)
  ("r3",   0.00, "MANUAL_REVIEW"),    # cap reached
]
```

---
